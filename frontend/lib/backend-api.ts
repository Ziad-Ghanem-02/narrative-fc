import type {
  EvaluationResponse,
  StoryJobResponse,
  StoryResponse,
  StoryRevisionResponse,
} from "@/lib/story-types";


const apiBaseUrl = "/api/backend";


function errorDetail(payload: unknown): string | undefined {
  if (
    typeof payload === "object" &&
    payload !== null &&
    "detail" in payload &&
    typeof payload.detail === "string"
  ) {
    return payload.detail;
  }
}


async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  const payload = (await response.json()) as unknown;
  if (!response.ok) {
    throw new Error(errorDetail(payload) ?? "The backend request failed.");
  }

  return payload as T;
}


export function queueStoryGeneration(question: string): Promise<StoryJobResponse> {
  return request<StoryJobResponse>("/story-jobs/", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

export function getStoryJob(jobId: string): Promise<StoryJobResponse> {
  return request<StoryJobResponse>(`/story-jobs/${jobId}/`);
}


export function getStory(storyId: string): Promise<StoryResponse> {
  return request<StoryResponse>(`/stories/${storyId}/`);
}

export function getLatestStory(): Promise<StoryResponse> {
  return request<StoryResponse>("/stories/latest/");
}

export function reviseStory(
  storyId: string,
  instruction: string,
): Promise<StoryRevisionResponse> {
  return request<StoryRevisionResponse>(`/stories/${storyId}/revisions/`, {
    method: "POST",
    body: JSON.stringify({ instruction }),
  });
}

export interface EvaluationSubmission {
  story_id: string;
  clarity_a: number;
  clarity_b: number;
  trustworthiness_a: number;
  trustworthiness_b: number;
  evidence_a: number;
  evidence_b: number;
  insightfulness_a: number;
  insightfulness_b: number;
  engagement_a: number;
  engagement_b: number;
  preferred_story: "story_a" | "story_b" | "tie";
  feedback: string;
}

export function submitEvaluation(
  evaluation: EvaluationSubmission,
): Promise<EvaluationResponse> {
  return request<EvaluationResponse>("/evaluations/", {
    method: "POST",
    body: JSON.stringify(evaluation),
  });
}
