import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from story_pipeline.graph import run_story
from stories.models import StoryGeneration, StoryGenerationJob


logger = logging.getLogger(__name__)
STALE_JOB_TIMEOUT = timedelta(minutes=30)


def persist_story(final_state: dict) -> StoryGeneration:
    return StoryGeneration.objects.create(
        question=final_state["question"],
        queries=final_state["queries"],
        results=final_state["results"],
        evidence=final_state["evidence"],
        plan=final_state["plan"],
        original_story=final_state["story"],
        current_story=final_state["story"],
        charts=final_state["charts"],
    )


def requeue_stale_story_jobs() -> int:
    stale_before = timezone.now() - STALE_JOB_TIMEOUT
    return StoryGenerationJob.objects.filter(
        status=StoryGenerationJob.Status.PROCESSING,
        started_at__lt=stale_before,
    ).update(
        status=StoryGenerationJob.Status.QUEUED,
        started_at=None,
    )


def claim_next_story_job() -> StoryGenerationJob | None:
    with transaction.atomic():
        job = (
            StoryGenerationJob.objects.select_for_update(skip_locked=True)
            .filter(status=StoryGenerationJob.Status.QUEUED)
            .order_by("created_at")
            .first()
        )
        if not job:
            return None

        job.status = StoryGenerationJob.Status.PROCESSING
        job.started_at = timezone.now()
        job.error_message = ""
        job.save(update_fields=["status", "started_at", "error_message"])
        return job


def process_next_story_job() -> bool:
    job = claim_next_story_job()
    if not job:
        return False

    try:
        story_generation = persist_story(run_story(job.question))
    except Exception as error:
        logger.exception("Story generation job %s failed.", job.id)
        StoryGenerationJob.objects.filter(
            pk=job.pk,
            status=StoryGenerationJob.Status.PROCESSING,
        ).update(
            status=StoryGenerationJob.Status.FAILED,
            error_message=f"{type(error).__name__}: {error}"[:2_000],
            completed_at=timezone.now(),
        )
    else:
        StoryGenerationJob.objects.filter(
            pk=job.pk,
            status=StoryGenerationJob.Status.PROCESSING,
        ).update(
            status=StoryGenerationJob.Status.SUCCEEDED,
            story_generation=story_generation,
            completed_at=timezone.now(),
        )

    return True
