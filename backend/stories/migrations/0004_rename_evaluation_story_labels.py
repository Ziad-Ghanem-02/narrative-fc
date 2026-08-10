from django.db import migrations, models


def migrate_preference_values(apps, schema_editor):
    StoryEvaluation = apps.get_model("stories", "StoryEvaluation")
    StoryEvaluation.objects.filter(preferred_story="story_a").update(
        preferred_story="agentic_story"
    )
    StoryEvaluation.objects.filter(preferred_story="story_b").update(
        preferred_story="human_written_story"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("stories", "0003_storyevaluation"),
    ]

    operations = [
        migrations.RenameField(
            model_name="storyevaluation",
            old_name="clarity_a",
            new_name="clarity_agentic_story",
        ),
        migrations.RenameField(
            model_name="storyevaluation",
            old_name="clarity_b",
            new_name="clarity_human_written_story",
        ),
        migrations.RenameField(
            model_name="storyevaluation",
            old_name="trustworthiness_a",
            new_name="trustworthiness_agentic_story",
        ),
        migrations.RenameField(
            model_name="storyevaluation",
            old_name="trustworthiness_b",
            new_name="trustworthiness_human_written_story",
        ),
        migrations.RenameField(
            model_name="storyevaluation",
            old_name="evidence_a",
            new_name="evidence_agentic_story",
        ),
        migrations.RenameField(
            model_name="storyevaluation",
            old_name="evidence_b",
            new_name="evidence_human_written_story",
        ),
        migrations.RenameField(
            model_name="storyevaluation",
            old_name="insightfulness_a",
            new_name="insightfulness_agentic_story",
        ),
        migrations.RenameField(
            model_name="storyevaluation",
            old_name="insightfulness_b",
            new_name="insightfulness_human_written_story",
        ),
        migrations.RenameField(
            model_name="storyevaluation",
            old_name="engagement_a",
            new_name="engagement_agentic_story",
        ),
        migrations.RenameField(
            model_name="storyevaluation",
            old_name="engagement_b",
            new_name="engagement_human_written_story",
        ),
        migrations.AlterField(
            model_name="storyevaluation",
            name="preferred_story",
            field=models.CharField(
                choices=[
                    ("agentic_story", "Agentic story"),
                    ("human_written_story", "Human-written story"),
                    ("tie", "Tie"),
                ],
                max_length=19,
            ),
        ),
        migrations.RunPython(migrate_preference_values, migrations.RunPython.noop),
    ]
