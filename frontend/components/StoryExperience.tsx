"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { AgenticStory } from "@/components/AgenticStory";
import { getStory, getStoryJob, queueStoryGeneration } from "@/lib/backend-api";
import { humanStory } from "@/lib/human-story";
import type { StoryResponse } from "@/lib/story-types";


const defaultQuestion =
  "Has the competitive gap between traditional football powerhouses and underdog teams decreased in recent FIFA Men's World Cups?";


export function StoryExperience() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [question, setQuestion] = useState(defaultQuestion);
  const [story, setStory] = useState<StoryResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [generationStatus, setGenerationStatus] = useState("");

  useEffect(() => {
    const storyId = searchParams.get("story");
    if (!storyId || story?.id === storyId) {
      return;
    }

    let isCurrent = true;
    setIsLoading(true);
    setError("");

    void getStory(storyId)
      .then((response) => {
        if (isCurrent) {
          setStory(response);
          setQuestion(response.question);
        }
      })
      .catch((requestError: unknown) => {
        if (isCurrent) {
          setError(
            requestError instanceof Error
              ? requestError.message
              : "The saved story could not be loaded.",
          );
        }
      })
      .finally(() => {
        if (isCurrent) {
          setIsLoading(false);
        }
      });

    return () => {
      isCurrent = false;
    };
  }, [searchParams, story?.id]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError("");
    setGenerationStatus("Queueing story generation...");

    try {
      const job = await queueStoryGeneration(question);
      let jobStatus = job;

      while (
        jobStatus.status === "queued" ||
        jobStatus.status === "processing"
      ) {
        setGenerationStatus(
          jobStatus.status === "queued"
            ? "Story is queued for generation..."
            : "Generating story and visualizations...",
        );
        await new Promise((resolve) => setTimeout(resolve, 2_000));
        jobStatus = await getStoryJob(job.id);
      }

      if (jobStatus.status === "failed" || !jobStatus.story) {
        throw new Error(jobStatus.detail ?? "Story generation failed.");
      }

      setStory(jobStatus.story);
      router.replace(`/stories?story=${jobStatus.story.id}`);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Story generation failed.",
      );
    } finally {
      setIsLoading(false);
      setGenerationStatus("");
    }
  }

  return (
    <>
      <form className="panel mt-8 p-5" onSubmit={handleSubmit}>
        <label className="text-sm font-bold" htmlFor="research-question">
          Research question
        </label>
        <textarea
          className="mt-3 min-h-28 w-full rounded-lg border border-white/10 bg-[#07131c] p-4 text-sm leading-6 outline-none focus:border-[#efbc42]"
          id="research-question"
          onChange={(event) => setQuestion(event.target.value)}
          required
          value={question}
        />
        <button
          className="gold-button mt-4 px-6 py-3 text-sm disabled:cursor-wait disabled:opacity-60"
          disabled={isLoading}
          type="submit"
        >
          {isLoading ? "GENERATING STORY..." : "GENERATE STORY A"}
        </button>
        {generationStatus && (
          <p className="mt-3 text-sm text-slate-400">{generationStatus}</p>
        )}
        {error && <p className="mt-3 text-sm text-rose-300">{error}</p>}
      </form>

      <section className="mt-8 grid gap-5 lg:grid-cols-2">
        <article className="panel p-6 md:p-8">
          <h2 className="text-center text-sm font-bold uppercase tracking-[.18em] text-[#efbc42]">
            Story A · Agentic
          </h2>
          {story ? (
            <>
              <p className="mt-3 text-center text-xs text-slate-500">
                Persisted story ID: {story.id}
              </p>
              <div className="mt-6">
                <AgenticStory charts={story.charts} story={story.story} />
              </div>
            </>
          ) : (
            <p className="mt-6 text-center text-sm leading-7 text-slate-400">
              Generate Story A to see the agentic narrative and its data-backed
              visualizations.
            </p>
          )}
        </article>

        <article className="panel p-6 md:p-8">
          <h2 className="text-center text-sm font-bold uppercase tracking-[.18em] text-[#efbc42]">
            Story B · Human
          </h2>
          <p className="mt-3 text-center text-xs text-slate-500">
            Baseline version: {humanStory.version}
          </p>
          <div className="mt-6 space-y-5 text-sm leading-7 text-slate-200">
            {humanStory.paragraphs.map((paragraph) => (
              <p key={paragraph}>{paragraph}</p>
            ))}
          </div>
        </article>
      </section>
    </>
  );
}
