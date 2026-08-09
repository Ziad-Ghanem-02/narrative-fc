from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from story_pipeline.agents.data_agent import DataAgent
from story_pipeline.agents.evidence_builder import EvidenceBuilder
from story_pipeline.agents.visualization_agent import VisualizationAgent
from story_pipeline.serialization import to_json_value
from stories.models import StoryGeneration, StoryRevision


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

    def test_rejects_missing_question(self):
        response = self.client.post("/api/stories/", {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("question", response.data)

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

    def test_returns_chart_data_without_creating_files(self):
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
            result["charts"],
            [
                {
                    "title": "Goals scored comparison",
                    "columns": ["year", "goals"],
                    "data": [{"year": 2022, "goals": 172}],
                }
            ],
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
