from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient

from story_pipeline.agents.data_agent import DataAgent
from story_pipeline.agents.visualization_agent import VisualizationAgent

class StoryGenerationViewTests(SimpleTestCase):
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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["story"], "Story")
        run_story.assert_called_once_with("Did underdogs close the gap?")

    def test_rejects_missing_question(self):
        response = self.client.post("/api/stories/", {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("question", response.data)

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
