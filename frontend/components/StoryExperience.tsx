"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { ArrowRight } from "lucide-react";

import { AgenticStory } from "@/components/AgenticStory";
import { HumanStory } from "@/components/HumanStory";
import {
  getLatestStory,
  getStory,
  getStoryJob,
  queueStoryGeneration,
  reviseStory,
} from "@/lib/backend-api";
import type { StoryResponse } from "@/lib/story-types";


const defaultQuestion =
  "Has the competitive gap between traditional football powerhouses and underdog teams decreased in recent FIFA Men's World Cups?";


export function StoryExperience() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [question, setQuestion] = useState(defaultQuestion);
  const [story, setStory] = useState<StoryResponse | null>(null);
  const [error, setError] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStatus, setGenerationStatus] = useState("");

  useEffect(() => {
    const storyId = searchParams.get("story");
    if (storyId && story?.id === storyId) {
      return;
    }

    let isCurrent = true;
    setError("");

    const storyRequest = storyId ? getStory(storyId) : getLatestStory();

    void storyRequest
      .then((response) => {
        if (isCurrent) {
          setStory(response);
          setQuestion(response.question);
          if (!storyId) {
            router.replace(`/stories?story=${response.id}`);
          }
        }
      })
      .catch((requestError: unknown) => {
        if (isCurrent) {
          if (
            !storyId &&
            requestError instanceof Error &&
            requestError.message === "No generated stories exist yet."
          ) {
            setStory(null);
            return;
          }
          setError(
            requestError instanceof Error
              ? requestError.message
              : "The saved story could not be loaded.",
          );
        }
      });

    return () => {
      isCurrent = false;
    };
  }, [router, searchParams, story?.id]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsGenerating(true);
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
      setIsGenerating(false);
      setGenerationStatus("");
    }
  }

  async function handleRewrite(instruction: string) {
    if (!story) {
      throw new Error("No story is available to rewrite.");
    }

    const revision = await reviseStory(story.id, instruction);
    setStory((previous) => {
      if (!previous || previous.id !== revision.story_id) {
        return previous;
      }

      return {
        ...previous,
        story: revision.story,
        // Keep the original chart data and metadata untouched.
        charts: previous.charts,
        updated_at: revision.created_at,
      };
    });
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
          className="gold-button mt-4 px-6 py-3 text-sm disabled:cursor-not-allowed disabled:opacity-60"
          disabled={isGenerating} // UNCOMMENT THIS LINE AND COMMENT NEXT ONE TO ENABLE SUBMISSIONS
          // disabled={true}
          type="submit"
        >
          {isGenerating ? "GENERATING AGENTIC STORY..." : "GENERATE AGENTIC STORY"}
        </button>
        {generationStatus && (
          <p className="mt-3 text-sm text-slate-400">{generationStatus}</p>
        )}
        {error && <p className="mt-3 text-sm text-rose-300">{error}</p>}
      </form>

      {story ? (
        <div className="mt-8">
          <AgenticStory
            charts={story.charts}
            onRewrite={handleRewrite}
            story={story.story}
            storyId={story.id}
          />
        </div>
      ) : (
        <section className="panel mt-8 p-6 text-center text-sm leading-7 text-slate-400">
          Generate the agentic story to see its data-backed
          visualizations.
        </section>
      )}

      <div className="mt-5">
        <HumanStory />
      </div>

      <div className="mt-10 flex justify-end">
        <Link
          className="gold-button inline-flex items-center gap-3 px-7 py-4 text-sm"
          href={`/evaluation?story=${story?.id ?? ""}`}
          aria-disabled={!story}
          onClick={(event) => {
            if (!story) event.preventDefault();
          }}
        >
          NEXT: RATE THE STORIES <ArrowRight size={18} />
        </Link>
      </div>
    </>
  );
}
