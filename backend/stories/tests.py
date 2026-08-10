from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from story_pipeline.agents.data_agent import DataAgent
from story_pipeline.agents.evidence_builder import EvidenceBuilder
from story_pipeline.agents.visualization_agent import VisualizationAgent
from story_pipeline.charts import build_chart_specs
from story_pipeline.graph import create_graph
from story_pipeline.serialization import to_json_value
from story_pipeline.story_links import retain_valid_chart_markers
from story_pipeline.world_cup import load_map_summary
from stories.models import StoryEvaluation, StoryGeneration, StoryGenerationJob, StoryRevision
from stories.services import process_next_story_job


class StoryGenerationViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_generates_story_from_question(self):
        final_state = {
            "question": "Did underdogs close the gap?",
            "queries": [{"purpose": "Goals", "sql": "SELECT 1"}],
            "results": [{"purpose": "Goals", "sql": "SELECT 1", "columns": ["value"], "data": [{"value": 1}]}],
            "evidence": "Evidence",
            "plan": "Plan",
            "story": "Story",
            "charts": [
                {
                    "title": "Goals",
                    "columns": ["value"],
                    "data": [{"value": 1}],
                }
            ],
        }

        with patch("stories.views.run_story", return_value=final_state) as run_story:
            response = self.client.post(
                "/api/stories/",
                {"question": "Did underdogs close the gap?"},
                format="json",
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["story"], "Story")
        self.assertEqual(StoryGeneration.objects.count(), 1)
        run_story.assert_called_once_with("Did underdogs close the gap?")

    @patch("stories.views.load_map_summary")
    def test_returns_live_map_summary(self, load_map_summary):
        load_map_summary.return_value = [
            {
                "name": "Brazil",
                "wins": 76,
                "draws": 19,
                "losses": 19,
                "matches": 114,
                "peak_stage": "Champions",
                "confederation": "CONMEBOL",
            }
        ]

        response = self.client.get("/api/world-cup/map-summary/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["countries"], load_map_summary.return_value)

    @patch("story_pipeline.world_cup.run_query_with_columns")
    def test_load_map_summary_returns_json_ready_country_stats(
        self,
        run_query_with_columns,
    ):
        run_query_with_columns.return_value = (
            [
                "name",
                "wins",
                "draws",
                "losses",
                "matches",
                "peak_stage",
                "confederation",
            ],
            [("Egypt", 2, 2, 1, 5, "Round of 16", "CAF")],
        )

        self.assertEqual(
            load_map_summary(),
            [
                {
                    "name": "Egypt",
                    "wins": 2,
                    "draws": 2,
                    "losses": 1,
                    "matches": 5,
                    "peak_stage": "Round of 16",
                    "confederation": "CAF",
                }
            ],
        )

    def test_rejects_missing_question(self):
        response = self.client.post("/api/stories/", {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("question", response.data)

    def test_accepts_anonymous_story_evaluation(self):
        story_generation = StoryGeneration.objects.create(
            question="Did underdogs close the gap?",
            queries=[],
            results=[],
            evidence="Evidence",
            plan="Plan",
            original_story="Story A",
            current_story="Story A",
            charts=[],
        )
        ratings = {
            "clarity_a": 4,
            "clarity_b": 3,
            "trustworthiness_a": 5,
            "trustworthiness_b": 4,
            "evidence_a": 5,
            "evidence_b": 3,
            "insightfulness_a": 4,
            "insightfulness_b": 4,
            "engagement_a": 3,
            "engagement_b": 5,
        }

        response = self.client.post(
            "/api/evaluations/",
            {
                "story_id": str(story_generation.id),
                **ratings,
                "preferred_story": "story_b",
                "feedback": "The human story was more engaging.",
            },
            format="json",
        )

        evaluation = StoryEvaluation.objects.get()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(evaluation.story_generation, story_generation)
        self.assertEqual(evaluation.preferred_story, "story_b")
        self.assertEqual(evaluation.feedback, "The human story was more engaging.")

    def test_rejects_evaluation_rating_outside_scale(self):
        story_generation = StoryGeneration.objects.create(
            question="Question",
            queries=[],
            results=[],
            evidence="Evidence",
            plan="Plan",
            original_story="Story A",
            current_story="Story A",
            charts=[],
        )
        response = self.client.post(
            "/api/evaluations/",
            {
                "story_id": str(story_generation.id),
                "clarity_a": 6,
                "clarity_b": 3,
                "trustworthiness_a": 3,
                "trustworthiness_b": 3,
                "evidence_a": 3,
                "evidence_b": 3,
                "insightfulness_a": 3,
                "insightfulness_b": 3,
                "engagement_a": 3,
                "engagement_b": 3,
                "preferred_story": "tie",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("clarity_a", response.data)
        self.assertEqual(StoryEvaluation.objects.count(), 0)

    def test_queues_story_generation_job(self):
        response = self.client.post(
            "/api/story-jobs/",
            {"question": "Did underdogs close the gap?"},
            format="json",
        )

        job = StoryGenerationJob.objects.get()
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data["id"], job.id)
        self.assertEqual(job.status, StoryGenerationJob.Status.QUEUED)

    @patch("stories.services.run_story")
    def test_worker_persists_story_and_marks_job_succeeded(self, run_story):
        job = StoryGenerationJob.objects.create(
            question="Did underdogs close the gap?",
        )
        run_story.return_value = {
            "question": job.question,
            "queries": [],
            "results": [],
            "evidence": "Evidence",
            "plan": "Plan",
            "story": "Story",
            "charts": [],
        }

        self.assertTrue(process_next_story_job())

        job.refresh_from_db()
        self.assertEqual(job.status, StoryGenerationJob.Status.SUCCEEDED)
        self.assertEqual(job.story_generation.current_story, "Story")
        run_story.assert_called_once_with(job.question)

    @patch("stories.services.run_story", side_effect=RuntimeError("LLM unavailable"))
    def test_worker_marks_failed_job_without_losing_it(self, _run_story):
        job = StoryGenerationJob.objects.create(question="Test question")

        self.assertTrue(process_next_story_job())

        job.refresh_from_db()
        self.assertEqual(job.status, StoryGenerationJob.Status.FAILED)
        self.assertIn("LLM unavailable", job.error_message)

    def test_returns_succeeded_job_story(self):
        story_generation = StoryGeneration.objects.create(
            question="Did underdogs close the gap?",
            queries=[],
            results=[],
            evidence="Evidence",
            plan="Plan",
            original_story="Story",
            current_story="Story",
            charts=[],
        )
        job = StoryGenerationJob.objects.create(
            question=story_generation.question,
            status=StoryGenerationJob.Status.SUCCEEDED,
            story_generation=story_generation,
        )

        response = self.client.get(f"/api/story-jobs/{job.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], StoryGenerationJob.Status.SUCCEEDED)
        self.assertEqual(response.data["story"]["id"], story_generation.id)

    def test_rewrites_story_and_persists_revision(self):
        story_generation = StoryGeneration.objects.create(
            question="Did underdogs close the gap?",
            queries=[],
            results=[],
            evidence="Underdogs improved their tournament results.",
            plan="Discuss tournament results.",
            original_story="The original story.",
            current_story="The original story.",
            charts=[],
        )

        with patch(
            "stories.views.StoryRewriter.rewrite",
            return_value="The revised, more optimistic story.",
        ) as rewrite:
            response = self.client.post(
                f"/api/stories/{story_generation.id}/revisions/",
                {"instruction": "Make the story more optimistic."},
                format="json",
            )

        story_generation.refresh_from_db()
        revision = StoryRevision.objects.get()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["revision_number"], 1)
        self.assertEqual(story_generation.current_story, revision.story)
        rewrite.assert_called_once_with(
            question=story_generation.question,
            evidence=story_generation.evidence,
            story="The original story.",
            charts=[],
            instruction="Make the story more optimistic.",
        )

    def test_converts_postgresql_values_for_json_storage(self):
        value = {
            "average": Decimal("1.75"),
            "nested": (Decimal("2.5"),),
        }

        self.assertEqual(
            to_json_value(value),
            {"average": 1.75, "nested": [2.5]},
        )

    @patch("story_pipeline.agents.evidence_builder.run_query_with_columns")
    @patch("story_pipeline.agents.evidence_builder.ask_llm", return_value="Evidence")
    def test_evidence_builder_normalizes_decimal_query_results(
        self,
        _ask_llm,
        run_query_with_columns,
    ):
        run_query_with_columns.return_value = (
            ["average_goal_difference"],
            [(Decimal("1.75"),)],
        )

        result = EvidenceBuilder()(
            {
                "question": "How competitive were the tournaments?",
                "queries": [{"purpose": "Goal difference", "sql": "SELECT 1"}],
            }
        )

        self.assertEqual(
            result["results"][0]["data"],
            [{"average_goal_difference": 1.75}],
        )

    @patch("story_pipeline.agents.visualization_agent.ask_llm")
    def test_returns_validated_recharts_specification(self, ask_llm):
        ask_llm.return_value = """
        [
          {
            "type": "line",
            "title": "Goals by tournament",
            "description": "A comparison over time.",
            "x_axis": {"data_key": "year", "label": "World Cup year"},
            "y_axis": {"label": "Goals", "format": "number"},
            "series": [
              {
                "data_key": "goals",
                "label": "Goals",
                "render_as": "line"
              }
            ]
          }
        ]
        """
        result = VisualizationAgent()(
            {
                "results": [
                    {
                        "purpose": "Goals scored comparison",
                        "columns": ["year", "goals"],
                        "data": [{"year": 2022, "goals": 172}],
                    }
                ]
            }
        )

        self.assertEqual(
            result["charts"][0],
            {
                "id": "chart-1",
                "type": "line",
                "title": "Goals by tournament",
                "description": "A comparison over time.",
                "x_axis": {"data_key": "year", "label": "World Cup year"},
                "y_axis": {"label": "Goals", "format": "number"},
                "series": [
                    {
                        "data_key": "goals",
                        "label": "Goals",
                        "color": "#EAB308",
                        "render_as": "line",
                    }
                ],
                "data": [{"year": 2022, "goals": 172}],
            },
        )

    def test_falls_back_for_invalid_chart_specification(self):
        charts = build_chart_specs(
            [
                {
                    "purpose": "Goals scored comparison",
                    "columns": ["year", "goals"],
                    "data": [{"year": 2022, "goals": 172}],
                }
            ],
            [
                {
                    "type": "pie",
                    "title": "Invalid",
                    "description": "",
                    "x_axis": {"data_key": "year", "label": "Year"},
                    "y_axis": {"label": "Value", "format": "number"},
                    "series": [],
                }
            ],
        )

        self.assertEqual(charts[0]["type"], "line")
        self.assertEqual(charts[0]["series"][0]["data_key"], "goals")

    def test_removes_unknown_chart_links_from_story(self):
        story = (
            "A valid claim. [chart:chart-1-goals] "
            "An invalid claim. [chart:not-returned]"
        )

        self.assertEqual(
            retain_valid_chart_markers(story, [{"id": "chart-1-goals"}]),
            "A valid claim. [chart:chart-1-goals] An invalid claim.",
        )

    def test_normalizes_legacy_chart_links_from_existing_stories(self):
        self.assertEqual(
            retain_valid_chart_markers(
                "A valid claim. [chart-1-legacy-purpose]",
                [{"id": "chart-1-legacy-purpose"}],
            ),
            "A valid claim. [chart:chart-1-legacy-purpose]",
        )

    @patch("story_pipeline.graph.load_schema", return_value={})
    def test_waits_for_charts_before_writing_story(self, _load_schema):
        graph = create_graph()

        self.assertTrue(
            any(
                edge.source == "visualizer" and edge.target == "writer"
                for edge in graph.get_graph().edges
            )
        )

    def test_parses_purpose_on_its_own_line(self):
        queries = DataAgent({}).parse_queries(
            """
            PURPOSE:
            Goals scored comparison between Big Teams and Underdogs.

            SQL:
            SELECT 1 AS value;
            ###
            PURPOSE: Quarter-final representation
            SQL: SELECT 2 AS value;
            """
        )

        self.assertEqual(
            queries,
            [
                {
                    "purpose": "Goals scored comparison between Big Teams and Underdogs.",
                    "sql": "SELECT 1 AS value;",
                },
                {
                    "purpose": "Quarter-final representation",
                    "sql": "SELECT 2 AS value;",
                },
            ],
        )
