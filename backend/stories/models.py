import uuid

from django.db import models


class StoryGeneration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField()
    queries = models.JSONField()
    results = models.JSONField()
    evidence = models.TextField()
    plan = models.TextField()
    original_story = models.TextField()
    current_story = models.TextField()
    charts = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StoryGenerationJob(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        PROCESSING = "processing", "Processing"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField()
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.QUEUED,
    )
    story_generation = models.OneToOneField(
        StoryGeneration,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generation_job",
    )
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class StoryRevision(models.Model):
    story_generation = models.ForeignKey(
        StoryGeneration,
        on_delete=models.CASCADE,
        related_name="revisions",
    )
    number = models.PositiveIntegerField()
    instruction = models.TextField()
    story = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["story_generation", "number"],
                name="unique_story_revision_number",
            )
        ]


class StoryEvaluation(models.Model):
    class PreferredStory(models.TextChoices):
        AGENTIC_STORY = "agentic_story", "Agentic story"
        HUMAN_WRITTEN_STORY = "human_written_story", "Human-written story"
        TIE = "tie", "Tie"

    story_generation = models.ForeignKey(
        StoryGeneration,
        on_delete=models.CASCADE,
        related_name="evaluations",
    )
    clarity_agentic_story = models.PositiveSmallIntegerField()
    clarity_human_written_story = models.PositiveSmallIntegerField()
    trustworthiness_agentic_story = models.PositiveSmallIntegerField()
    trustworthiness_human_written_story = models.PositiveSmallIntegerField()
    evidence_agentic_story = models.PositiveSmallIntegerField()
    evidence_human_written_story = models.PositiveSmallIntegerField()
    insightfulness_agentic_story = models.PositiveSmallIntegerField()
    insightfulness_human_written_story = models.PositiveSmallIntegerField()
    engagement_agentic_story = models.PositiveSmallIntegerField()
    engagement_human_written_story = models.PositiveSmallIntegerField()
    preferred_story = models.CharField(max_length=19, choices=PreferredStory.choices)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
