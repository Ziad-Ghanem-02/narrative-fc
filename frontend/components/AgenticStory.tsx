"use client";

import { FormEvent, type ReactNode, useEffect, useRef, useState } from "react";

import { BackendChart } from "@/components/BackendChart";
import type { ChartSpec } from "@/lib/story-types";


interface AgenticStoryProps {
  story: string;
  charts: ChartSpec[];
  storyId: string;
  onRewrite: (instruction: string) => Promise<void>;
}


const chartMarker = /\[(?:chart:([a-z0-9-]+)|(chart-[a-z0-9-]+))\]/g;


export function AgenticStory({
  story,
  charts,
  storyId,
  onRewrite,
}: AgenticStoryProps) {
  const [activeChartId, setActiveChartId] = useState(charts[0]?.id ?? "");
  const [instruction, setInstruction] = useState("");
  const [rewriteError, setRewriteError] = useState("");
  const [isRewriting, setIsRewriting] = useState(false);
  const chartPanel = useRef<HTMLElement>(null);
  const chartsById = new Map(charts.map((chart) => [chart.id, chart]));
  const activeChart = chartsById.get(activeChartId) ?? charts[0];

  useEffect(() => {
    setActiveChartId(charts[0]?.id ?? "");
  }, [charts]);

  function activateChart(chartId: string, scrollOnMobile = false) {
    setActiveChartId(chartId);
    if (
      scrollOnMobile &&
      window.matchMedia("(max-width: 1023px)").matches
    ) {
      chartPanel.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  async function handleRewriteSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedInstruction = instruction.trim();
    if (!trimmedInstruction) {
      return;
    }

    setIsRewriting(true);
    setRewriteError("");
    try {
      await onRewrite(trimmedInstruction);
      setInstruction("");
    } catch (error) {
      setRewriteError(
        error instanceof Error
          ? error.message
          : "Story rewrite failed. Please try again.",
      );
    } finally {
      setIsRewriting(false);
    }
  }

  return (
    <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(360px,.8fr)]">
      <article className="panel min-w-0 p-6 md:p-8">
        <h2 className="text-center text-sm font-bold uppercase tracking-[.18em] text-[#efbc42]">
          Agentic story
        </h2>
        {/* <p className="mt-3 text-center text-xs text-slate-500">
          Persisted story ID: {storyId}
        </p> */}
        <form className="mt-5 rounded-xl border border-white/10 bg-white/[.02] p-4" onSubmit={handleRewriteSubmit}>
          <label className="text-xs font-bold uppercase tracking-[.14em] text-slate-400" htmlFor="story-rewrite-instruction">
            Rewrite agentic story
          </label>
          <textarea
            className="mt-2 min-h-20 w-full rounded-lg border border-white/10 bg-[#07131c] p-3 text-sm leading-6 text-slate-200 outline-none focus:border-[#efbc42]"
            id="story-rewrite-instruction"
            onChange={(event) => setInstruction(event.target.value)}
            placeholder="Example: make it shorter and more formal, keep all chart references accurate."
            value={instruction}
          />
          <button
            className="gold-button mt-3 px-4 py-2 text-xs disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isRewriting || !instruction.trim()} //UNCOMMENT AND COMMENT NEXT LINE TO ENABLE REWRITES
            // disabled={true}
            type="submit"
          >
            {isRewriting ? "REWRITING STORY..." : "REWRITE STORY TEXT"}
          </button>
          {rewriteError && <p className="mt-2 text-xs text-rose-300">{rewriteError}</p>}
        </form>
        <div className="mt-6 space-y-5 text-sm leading-7 text-slate-200">
          {story
            .split(/\n{2,}/)
            .filter(Boolean)
            .map((paragraph, index) => (
              <p key={index}>
                <ParagraphWithChartLinks
                  chartsById={chartsById}
                  onActivate={activateChart}
                  paragraph={paragraph.trim()}
                />
              </p>
            ))}
        </div>
      </article>

      <aside
        className="panel min-w-0 self-start p-5 lg:sticky lg:top-6"
        ref={chartPanel}
      >
        {activeChart ? (
          <>
            <p className="section-kicker">DATA EXPLORER</p>
            <h2 className="mt-2 text-lg font-bold">{activeChart.title}</h2>
            {activeChart.description && (
              <p className="mt-2 text-xs leading-5 text-slate-400">
                {activeChart.description}
              </p>
            )}
            <div className="mt-4 min-h-80">
              <BackendChart chart={activeChart} />
            </div>
            <ChartSelector
              activeChartId={activeChart.id}
              charts={charts}
              onSelect={(chartId) => activateChart(chartId, true)}
            />
          </>
        ) : (
          <p className="text-sm text-slate-400">
            No visual evidence was returned for this story.
          </p>
        )}
      </aside>
    </section>
  );
}


function ParagraphWithChartLinks({
  paragraph,
  chartsById,
  onActivate,
}: {
  paragraph: string;
  chartsById: Map<string, ChartSpec>;
  onActivate: (chartId: string, scrollOnMobile?: boolean) => void;
}) {
  const parts: ReactNode[] = [];
  let cursor = 0;

  for (const match of paragraph.matchAll(chartMarker)) {
    const [marker, canonicalChartId, legacyChartId] = match;
    const chartId = canonicalChartId ?? legacyChartId;
    const index = match.index ?? 0;
    parts.push(paragraph.slice(cursor, index));
    cursor = index + marker.length;

    const chart = chartsById.get(chartId);
    if (chart) {
      parts.push(
        <button
          aria-label={`Show visual: ${chart.title}`}
          className="ml-1 inline-flex items-center rounded-full border border-[#efbc42]/50 bg-[#efbc42]/10 px-2 py-0.5 text-xs font-bold text-[#f6cf63] transition hover:border-[#efbc42] hover:bg-[#efbc42]/20 focus:outline-none focus:ring-2 focus:ring-[#efbc42]"
          key={`${chartId}-${index}`}
          onClick={() => onActivate(chartId, true)}
          onFocus={() => onActivate(chartId)}
          onMouseEnter={() => onActivate(chartId)}
          type="button"
        >
          View visual
        </button>,
      );
    }
  }

  parts.push(paragraph.slice(cursor));
  return parts;
}


function ChartSelector({
  charts,
  activeChartId,
  onSelect,
}: {
  charts: ChartSpec[];
  activeChartId: string;
  onSelect: (chartId: string) => void;
}) {
  return (
    <div className="mt-4 border-t border-white/10 pt-4">
      <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
        Story visuals
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        {charts.map((chart, index) => (
          <button
            aria-pressed={chart.id === activeChartId}
            className={`rounded-full border px-2.5 py-1 text-xs transition ${
              chart.id === activeChartId
                ? "border-[#efbc42] bg-[#efbc42]/15 text-[#f6cf63]"
                : "border-white/10 text-slate-400 hover:border-white/30 hover:text-white"
            }`}
            key={chart.id}
            onClick={() => onSelect(chart.id)}
            type="button"
          >
            {index + 1}. {chart.title}
          </button>
        ))}
      </div>
    </div>
  );
}
