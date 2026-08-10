"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

import { BackendChart } from "@/components/BackendChart";
import { getHumanStoryVisuals } from "@/lib/backend-api";
import { humanStory } from "@/lib/human-story";
import type { ChartSpec } from "@/lib/story-types";

const chartMarker = /\[(?:chart:([a-z0-9-]+)|(chart-[a-z0-9-]+))\]/g;
const paragraphCharts: Record<number, string[]> = {
  0: ["chart-1"],
  2: ["chart-2", "chart-3"],
  4: ["chart-4"],
  6: ["chart-6", "chart-7"],
  8: ["chart-2", "chart-5", "chart-8"],
};

export function HumanStory() {
  const [charts, setCharts] = useState<ChartSpec[]>([]);
  const [error, setError] = useState("");
  const [activeChartId, setActiveChartId] = useState("");
  const chartPanel = useRef<HTMLElement>(null);
  const chartsById = new Map(charts.map((chart) => [chart.id, chart]));
  const activeChart = chartsById.get(activeChartId) ?? charts[0];

  useEffect(() => {
    let isCurrent = true;
    void getHumanStoryVisuals()
      .then((response) => {
        if (isCurrent) {
          setCharts(response.charts);
          setActiveChartId(response.charts[0]?.id ?? "");
        }
      })
      .catch((requestError: unknown) => {
        if (isCurrent) {
          setError(
            requestError instanceof Error
              ? requestError.message
              : "The human story visuals could not be loaded.",
          );
        }
      });

    return () => {
      isCurrent = false;
    };
  }, []);

  function activateChart(chartId: string, scrollOnMobile = false) {
    setActiveChartId(chartId);
    if (scrollOnMobile && window.matchMedia("(max-width: 1023px)").matches) {
      chartPanel.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  return (
    <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(360px,.8fr)]">
      <article className="panel min-w-0 p-6 md:p-8">
        <h2 className="text-center text-sm font-bold uppercase tracking-[.18em] text-[#efbc42]">
          Human-written story
        </h2>
        <p className="mt-3 text-center text-xs text-slate-500">
          Narrative with data references
        </p>
        <div className="mt-6 space-y-5 text-sm leading-7 text-slate-200">
          {humanStory.paragraphs.map((paragraph, index) => (
            <p key={index}>
              <ParagraphWithChartLinks
                chartsById={chartsById}
                onActivate={activateChart}
                paragraph={`${paragraph} ${(paragraphCharts[index] ?? [])
                  .map((chartId) => `[chart:${chartId}]`)
                  .join(" ")}`}
              />
            </p>
          ))}
        </div>
      </article>

      <aside className="panel min-w-0 self-start p-5 lg:sticky lg:top-6" ref={chartPanel}>
        {activeChart ? (
          <>
            <p className="section-kicker">DATA EXPLORER</p>
            <h2 className="mt-2 text-lg font-bold">{activeChart.title}</h2>
            {activeChart.description && (
              <p className="mt-2 text-xs leading-5 text-slate-400">{activeChart.description}</p>
            )}
            <div className="mt-4 min-h-80">
              <BackendChart chart={activeChart} />
            </div>
            <div className="mt-4 border-t border-white/10 pt-4">
              <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Story visuals</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {charts.map((chart, index) => (
                  <button
                    aria-pressed={chart.id === activeChart.id}
                    className={`rounded-full border px-2.5 py-1 text-xs transition ${
                      chart.id === activeChart.id
                        ? "border-[#efbc42] bg-[#efbc42]/15 text-[#f6cf63]"
                        : "border-white/10 text-slate-400 hover:border-white/30 hover:text-white"
                    }`}
                    key={chart.id}
                    onClick={() => activateChart(chart.id, true)}
                    type="button"
                  >
                    {index + 1}. {chart.title}
                  </button>
                ))}
              </div>
            </div>
          </>
        ) : (
          <p className="text-sm text-slate-400">
            {error || "Loading human story visuals..."}
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
