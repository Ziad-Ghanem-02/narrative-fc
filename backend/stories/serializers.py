from rest_framework import serializers


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
