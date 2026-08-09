from django.urls import path

from stories.views import StoryDetailView, StoryGenerationView, StoryRevisionView


urlpatterns = [
    path("stories/", StoryGenerationView.as_view(), name="story-generation"),
    path("stories/<uuid:story_id>/", StoryDetailView.as_view(), name="story-detail"),
    path(
        "stories/<uuid:story_id>/revisions/",
        StoryRevisionView.as_view(),
        name="story-revision",
    ),
]
