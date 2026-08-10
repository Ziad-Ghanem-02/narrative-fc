from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("stories", "0002_storygenerationjob"),
    ]

    operations = [
        migrations.CreateModel(
            name="StoryEvaluation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("clarity_a", models.PositiveSmallIntegerField()),
                ("clarity_b", models.PositiveSmallIntegerField()),
                ("trustworthiness_a", models.PositiveSmallIntegerField()),
                ("trustworthiness_b", models.PositiveSmallIntegerField()),
                ("evidence_a", models.PositiveSmallIntegerField()),
                ("evidence_b", models.PositiveSmallIntegerField()),
                ("insightfulness_a", models.PositiveSmallIntegerField()),
                ("insightfulness_b", models.PositiveSmallIntegerField()),
                ("engagement_a", models.PositiveSmallIntegerField()),
                ("engagement_b", models.PositiveSmallIntegerField()),
                (
                    "preferred_story",
                    models.CharField(
                        choices=[
                            ("story_a", "Story A"),
                            ("story_b", "Story B"),
                            ("tie", "Tie"),
                        ],
                        max_length=8,
                    ),
                ),
                ("feedback", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "story_generation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evaluations",
                        to="stories.storygeneration",
                    ),
                ),
            ],
        ),
    ]