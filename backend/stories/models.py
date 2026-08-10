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
        STORY_A = "story_a", "Story A"
        STORY_B = "story_b", "Story B"
        TIE = "tie", "Tie"

    story_generation = models.ForeignKey(
        StoryGeneration,
        on_delete=models.CASCADE,
        related_name="evaluations",
    )
    clarity_a = models.PositiveSmallIntegerField()
    clarity_b = models.PositiveSmallIntegerField()
    trustworthiness_a = models.PositiveSmallIntegerField()
    trustworthiness_b = models.PositiveSmallIntegerField()
    evidence_a = models.PositiveSmallIntegerField()
    evidence_b = models.PositiveSmallIntegerField()
    insightfulness_a = models.PositiveSmallIntegerField()
    insightfulness_b = models.PositiveSmallIntegerField()
    engagement_a = models.PositiveSmallIntegerField()
    engagement_b = models.PositiveSmallIntegerField()
    preferred_story = models.CharField(max_length=8, choices=PreferredStory.choices)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
