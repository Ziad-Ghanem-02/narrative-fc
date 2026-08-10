from django.urls import path

from stories.views import (
    LatestStoryDetailView,
    StoryDetailView,
    StoryGenerationView,
    StoryGenerationJobDetailView,
    StoryGenerationJobView,
    StoryRevisionView,
    WorldCupMapSummaryView,
)


urlpatterns = [
    path(
        "world-cup/map-summary/",
        WorldCupMapSummaryView.as_view(),
        name="world-cup-map-summary",
    ),
    path(
        "story-jobs/",
        StoryGenerationJobView.as_view(),
        name="story-generation-job",
    ),
    path(
        "story-jobs/<uuid:job_id>/",
        StoryGenerationJobDetailView.as_view(),
        name="story-generation-job-detail",
    ),
    path("stories/", StoryGenerationView.as_view(), name="story-generation"),
    path("stories/latest/", LatestStoryDetailView.as_view(), name="latest-story-detail"),
    path("stories/<uuid:story_id>/", StoryDetailView.as_view(), name="story-detail"),
    path(
        "stories/<uuid:story_id>/revisions/",
        StoryRevisionView.as_view(),
        name="story-revision",
    ),
]
