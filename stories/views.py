from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from story_pipeline.graph import run_story
from stories.serializers import StoryRequestSerializer


class StoryGenerationView(APIView):
    def post(self, request):
        serializer = StoryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        final_state = run_story(serializer.validated_data["question"])
        return Response(
            {
                "question": final_state["question"],
                "queries": final_state["queries"],
                "results": final_state["results"],
                "evidence": final_state["evidence"],
                "plan": final_state["plan"],
                "story": final_state["story"],
                "charts": final_state["charts"],
            },
            status=status.HTTP_200_OK,
        )
