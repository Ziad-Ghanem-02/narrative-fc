import type { StoryJobResponse, StoryResponse } from "@/lib/story-types";


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
