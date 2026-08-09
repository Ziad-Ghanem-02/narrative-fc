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
