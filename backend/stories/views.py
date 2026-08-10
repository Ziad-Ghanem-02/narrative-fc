import logging

from django.db import transaction
from django.db.models import Avg, Count, Max
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from story_pipeline.agents.story_rewriter import StoryRewriter
from story_pipeline.graph import run_story
from story_pipeline.human_story_visuals import load_human_story_visuals
from story_pipeline.story_links import retain_valid_chart_markers
from story_pipeline.world_cup import load_map_summary
from stories.models import StoryEvaluation, StoryGeneration, StoryGenerationJob, StoryRevision
from stories.serializers import (
    StoryEvaluationRequestSerializer,
    StoryRequestSerializer,
    StoryRevisionRequestSerializer,
)
from stories.services import persist_story


logger = logging.getLogger(__name__)


def story_response(story_generation: StoryGeneration) -> dict:
    return {
        "id": story_generation.id,
        "question": story_generation.question,
        "queries": story_generation.queries,
        "results": story_generation.results,
        "evidence": story_generation.evidence,
        "plan": story_generation.plan,
        "story": retain_valid_chart_markers(
            story_generation.current_story,
            story_generation.charts,
        ),
        "charts": story_generation.charts,
        "created_at": story_generation.created_at,
        "updated_at": story_generation.updated_at,
    }


class StoryGenerationView(APIView):
    def post(self, request):
        serializer = StoryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        final_state = run_story(serializer.validated_data["question"])
        story_generation = persist_story(final_state)
        return Response(
            story_response(story_generation),
            status=status.HTTP_201_CREATED,
        )


class WorldCupMapSummaryView(APIView):
    def get(self, request):
        return Response({"countries": load_map_summary()})


class HumanStoryVisualsView(APIView):
    def get(self, request):
        return Response(load_human_story_visuals())


class StoryGenerationJobView(APIView):
    def post(self, request):
        serializer = StoryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = StoryGenerationJob.objects.create(
            question=serializer.validated_data["question"],
        )
        return Response(
            {
                "id": job.id,
                "status": job.status,
                "created_at": job.created_at,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class StoryGenerationJobDetailView(APIView):
    def get(self, request, job_id):
        job = get_object_or_404(StoryGenerationJob, pk=job_id)
        response = {
            "id": job.id,
            "status": job.status,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
        }
        if job.status == StoryGenerationJob.Status.SUCCEEDED:
            response["story"] = story_response(job.story_generation)
        elif job.status == StoryGenerationJob.Status.FAILED:
            response["detail"] = "Story generation failed. Please try again."

        return Response(response)


class StoryDetailView(APIView):
    def get(self, request, story_id):
        story_generation = get_object_or_404(StoryGeneration, pk=story_id)
        response = story_response(story_generation)
        response["revisions"] = [
            {
                "id": revision.id,
                "number": revision.number,
                "instruction": revision.instruction,
                "story": revision.story,
                "created_at": revision.created_at,
            }
            for revision in story_generation.revisions.order_by("number")
        ]
        return Response(response)


class LatestStoryDetailView(APIView):
    def get(self, request):
        story_generation = StoryGeneration.objects.order_by("-created_at").first()
        if story_generation is None:
            return Response(
                {"detail": "No generated stories exist yet."},
                status=status.HTTP_404_NOT_FOUND,
            )

        response = story_response(story_generation)
        response["revisions"] = [
            {
                "id": revision.id,
                "number": revision.number,
                "instruction": revision.instruction,
                "story": revision.story,
                "created_at": revision.created_at,
            }
            for revision in story_generation.revisions.order_by("number")
        ]
        return Response(response)


class StoryRevisionView(APIView):
    def post(self, request, story_id):
        serializer = StoryRevisionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        story_generation = get_object_or_404(StoryGeneration, pk=story_id)
        instruction = serializer.validated_data["instruction"]
        try:
            revised_story = StoryRewriter().rewrite(
                question=story_generation.question,
                evidence=story_generation.evidence,
                story=story_generation.current_story,
                charts=story_generation.charts,
                instruction=instruction,
            )
        except Exception as error:
            logger.exception("Story revision failed for story %s.", story_id)
            return Response(
                {"detail": f"Story revision failed: {error}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        with transaction.atomic():
            story_generation = StoryGeneration.objects.select_for_update().get(pk=story_id)
            revision_number = (
                story_generation.revisions.aggregate(max_number=Max("number"))["max_number"]
                or 0
            ) + 1
            revision = StoryRevision.objects.create(
                story_generation=story_generation,
                number=revision_number,
                instruction=instruction,
                story=revised_story,
            )
            story_generation.current_story = revised_story
            story_generation.save(update_fields=["current_story", "updated_at"])

        return Response(
            {
                "story_id": story_generation.id,
                "revision_id": revision.id,
                "revision_number": revision.number,
                "instruction": revision.instruction,
                "story": revision.story,
                "created_at": revision.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class StoryEvaluationView(APIView):
    def post(self, request):
        serializer = StoryEvaluationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        evaluation = serializer.save()
        return Response(
            {"id": evaluation.id, "created_at": evaluation.created_at},
            status=status.HTTP_201_CREATED,
        )


class StoryEvaluationResultsView(APIView):
    def get(self, request):
        evaluations = StoryEvaluation.objects.all()
        averages = evaluations.aggregate(
            clarity_agentic_story=Avg("clarity_agentic_story"),
            clarity_human_written_story=Avg("clarity_human_written_story"),
            trustworthiness_agentic_story=Avg("trustworthiness_agentic_story"),
            trustworthiness_human_written_story=Avg("trustworthiness_human_written_story"),
            evidence_agentic_story=Avg("evidence_agentic_story"),
            evidence_human_written_story=Avg("evidence_human_written_story"),
            insightfulness_agentic_story=Avg("insightfulness_agentic_story"),
            insightfulness_human_written_story=Avg("insightfulness_human_written_story"),
            engagement_agentic_story=Avg("engagement_agentic_story"),
            engagement_human_written_story=Avg("engagement_human_written_story"),
        )

        def score(story_type, criterion):
            value = averages[f"{criterion}_{story_type}"]
            return round(float(value), 2) if value is not None else None

        return Response(
            {
                "total_evaluations": evaluations.count(),
                "preferences": {
                    "agentic_story": evaluations.filter(
                        preferred_story=StoryEvaluation.PreferredStory.AGENTIC_STORY
                    ).count(),
                    "human_written_story": evaluations.filter(
                        preferred_story=StoryEvaluation.PreferredStory.HUMAN_WRITTEN_STORY
                    ).count(),
                    "tie": evaluations.filter(
                        preferred_story=StoryEvaluation.PreferredStory.TIE
                    ).count(),
                },
                "scores": {
                    "agentic_story": {
                        criterion: score("agentic_story", criterion)
                        for criterion in (
                            "clarity",
                            "trustworthiness",
                            "evidence",
                            "insightfulness",
                            "engagement",
                        )
                    },
                    "human_written_story": {
                        criterion: score("human_written_story", criterion)
                        for criterion in (
                            "clarity",
                            "trustworthiness",
                            "evidence",
                            "insightfulness",
                            "engagement",
                        )
                    },
                },
                "reviews": [
                    {
                        "feedback": evaluation.feedback,
                        "preferred_story": evaluation.preferred_story,
                        "created_at": evaluation.created_at,
                    }
                    for evaluation in evaluations.exclude(feedback="")
                    .order_by("-created_at")[:100]
                ],
            }
        )
