from django.urls import path

from stories.views import (
    LatestStoryDetailView,
    StoryDetailView,
    StoryGenerationView,
    StoryGenerationJobDetailView,
    StoryGenerationJobView,
    StoryEvaluationView,
    StoryEvaluationResultsView,
    HumanStoryVisualsView,
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
        "world-cup/human-story-visuals/",
        HumanStoryVisualsView.as_view(),
        name="human-story-visuals",
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
    path("evaluations/", StoryEvaluationView.as_view(), name="story-evaluation"),
    path("evaluations/results/", StoryEvaluationResultsView.as_view(), name="story-evaluation-results"),
    path("stories/latest/", LatestStoryDetailView.as_view(), name="latest-story-detail"),
    path("stories/<uuid:story_id>/", StoryDetailView.as_view(), name="story-detail"),
    path(
        "stories/<uuid:story_id>/revisions/",
        StoryRevisionView.as_view(),
        name="story-revision",
    ),
]
