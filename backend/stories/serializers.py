from rest_framework import serializers

from stories.models import StoryEvaluation


class StoryRequestSerializer(serializers.Serializer):
    question = serializers.CharField(trim_whitespace=True, max_length=5_000)

    def validate_question(self, value: str) -> str:
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value


class StoryRevisionRequestSerializer(serializers.Serializer):
    instruction = serializers.CharField(trim_whitespace=True, max_length=2_000)

    def validate_instruction(self, value: str) -> str:
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value


class StoryEvaluationRequestSerializer(serializers.ModelSerializer):
    story_id = serializers.UUIDField(write_only=True)
    feedback = serializers.CharField(required=False, allow_blank=True, max_length=5_000)

    class Meta:
        model = StoryEvaluation
        fields = [
            "story_id",
            "clarity_a",
            "clarity_b",
            "trustworthiness_a",
            "trustworthiness_b",
            "evidence_a",
            "evidence_b",
            "insightfulness_a",
            "insightfulness_b",
            "engagement_a",
            "engagement_b",
            "preferred_story",
            "feedback",
        ]

    def validate_story_id(self, value):
        story_model = StoryEvaluation._meta.get_field("story_generation").related_model
        if not story_model.objects.filter(id=value).exists():
            raise serializers.ValidationError("The evaluated story does not exist.")
        return value

    def validate(self, attrs):
        for field_name in self.Meta.fields[1:11]:
            value = attrs.get(field_name)
            if value is None or not 1 <= value <= 5:
                raise serializers.ValidationError(
                    {field_name: "Choose a rating from 1 to 5 stars."}
                )
        return attrs

    def create(self, validated_data):
        story_id = validated_data.pop("story_id")
        return StoryEvaluation.objects.create(
            story_generation_id=story_id,
            **validated_data,
        )
