from django.urls import path

from stories.views import StoryGenerationView


urlpatterns = [
    path("stories/", StoryGenerationView.as_view(), name="story-generation"),
]
