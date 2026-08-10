"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowLeft, BarChart3, MessageSquareQuote, Star, Trophy } from "lucide-react";

import { getEvaluationResults } from "@/lib/backend-api";
import type { EvaluationResultsResponse, EvaluationScores } from "@/lib/story-types";

const criteria: Array<[keyof EvaluationScores, string]> = [
  ["clarity", "Clarity"],
  ["trustworthiness", "Trustworthiness"],
  ["evidence", "Use of evidence"],
  ["insightfulness", "Insightfulness"],
  ["engagement", "Engagement"],
];

function average(scores: EvaluationScores) {
  const values = Object.values(scores).filter((value): value is number => value !== null);
  return values.length ? values.reduce((total, value) => total + value, 0) / values.length : null;
}

function scoreText(value: number | null) {
  return value === null ? "-" : value.toFixed(2);
}

function PartialStars({ label, value }: { label: string; value: number | null }) {
  return (
    <div
      className="flex gap-1 text-[#efbc42]"
      aria-label={`${label} average rating ${scoreText(value)} out of 5`}
    >
      {[1, 2, 3, 4, 5].map((star) => {
        const fill = Math.min(100, Math.max(0, ((value ?? 0) - star + 1) * 100));
        return (
          <span className="relative block h-[15px] w-[15px]" key={star}>
            <Star className="absolute inset-0 text-slate-600" size={15} />
            <span className="absolute inset-0 overflow-hidden" style={{ width: `${fill}%` }}>
              <Star className="max-w-none fill-current text-[#efbc42]" size={15} />
            </span>
          </span>
        );
      })}
    </div>
  );
}

function preferenceLabel(preference: "agentic_story" | "human_written_story" | "tie") {
  return preference === "agentic_story"
    ? "Preferred agentic story"
    : preference === "human_written_story"
      ? "Preferred human-written story"
      : "No story preference";
}

export default function Reviews() {
  const [results, setResults] = useState<EvaluationResultsResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let isCurrent = true;
    void getEvaluationResults()
      .then((response) => {
        if (isCurrent) setResults(response);
      })
      .catch((requestError: unknown) => {
        if (isCurrent) {
          setError(requestError instanceof Error ? requestError.message : "The evaluation results could not be loaded.");
        }
      });
    return () => {
      isCurrent = false;
    };
  }, []);

  return (
    <main className="page-shell min-h-screen py-8 md:py-12">
      <div className="container-page">
        <Link aria-label="Back to evaluation" className="panel inline-flex p-3 text-slate-300 hover:text-white" href="/evaluation">
          <ArrowLeft size={20} />
        </Link>
        <header className="text-center">
          <p className="section-kicker mt-5">ANONYMOUS FEEDBACK</p>
          <h1 className="mt-2 text-2xl font-bold uppercase tracking-wide">Reader Ratings</h1>
          <div className="title-line" />
          <p className="mx-auto mt-5 max-w-xl text-sm text-slate-300">
            See how readers compare the agentic story with the human-written story.
          </p>
        </header>

        {error ? (
          <div className="panel mt-8 p-6 text-center text-sm text-rose-300">{error}</div>
        ) : results ? (
          <Results results={results} />
        ) : (
          <div className="panel mt-8 p-6 text-center text-sm text-slate-400">Loading reader ratings...</div>
        )}
      </div>
    </main>
  );
}

function Results({ results }: { results: EvaluationResultsResponse }) {
  const agenticAverage = average(results.scores.agentic_story);
  const humanAverage = average(results.scores.human_written_story);

  return (
    <>
      <section className="mt-8 grid gap-5 md:grid-cols-3">
        <SummaryCard icon={BarChart3} label="Evaluations" value={String(results.total_evaluations)} />
        <SummaryCard icon={Trophy} label="Agentic story preferred" value={String(results.preferences.agentic_story)} />
        <SummaryCard icon={Trophy} label="Human-written story preferred" value={String(results.preferences.human_written_story)} />
      </section>

      <section className="panel mt-5 overflow-hidden">
        <div className="grid grid-cols-1 md:grid-cols-2">
          <ScoreColumn label="Agentic story" scores={results.scores.agentic_story} overall={agenticAverage} accent="text-[#efbc42]" />
          <ScoreColumn label="Human-written story" scores={results.scores.human_written_story} overall={humanAverage} accent="text-[#72c463]" />
        </div>
      </section>

      <section className="panel mt-5 p-6">
        <div className="flex items-center gap-3">
          <MessageSquareQuote className="text-[#efbc42]" />
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider">Reader reviews</h2>
            <p className="mt-1 text-xs text-slate-500">Anonymous written feedback</p>
          </div>
        </div>
        {results.reviews.length ? (
          <div className="mt-5 space-y-3">
            {results.reviews.map((review, index) => (
              <blockquote className="border-l-2 border-[#efbc42]/60 bg-white/[.025] p-4 text-sm leading-6 text-slate-300" key={`${review.created_at}-${index}`}>
                <p className="mb-2 text-[11px] font-bold uppercase tracking-wider text-[#efbc42]">
                  {preferenceLabel(review.preferred_story)}
                </p>
                <p>“{review.feedback}”</p>
              </blockquote>
            ))}
          </div>
        ) : (
          <p className="mt-5 text-sm text-slate-400">No written reviews have been submitted yet.</p>
        )}
      </section>
    </>
  );
}

function SummaryCard({ icon: Icon, label, value }: { icon: typeof BarChart3; label: string; value: string }) {
  return (
    <article className="panel p-5 text-center">
      <Icon className="mx-auto text-[#efbc42]" size={22} />
      <p className="mt-3 text-2xl font-black">{value}</p>
      <p className="mt-1 text-xs font-bold uppercase text-slate-400">{label}</p>
    </article>
  );
}

function ScoreColumn({ label, scores, overall, accent }: { label: string; scores: EvaluationScores; overall: number | null; accent: string }) {
  return (
    <article className="p-6 md:p-8">
      <div className="flex items-center justify-between gap-4">
        <h2 className={`text-sm font-bold uppercase tracking-wider ${accent}`}>{label}</h2>
        <span className="text-lg font-black text-[#efbc42]">{scoreText(overall)} / 5</span>
      </div>
      <div className="mt-6 space-y-4">
        {criteria.map(([key, title]) => (
          <div key={key}>
            <div className="mb-1 flex justify-between text-xs text-slate-400">
              <span>{title}</span><span className="font-bold text-[#efbc42]">{scoreText(scores[key])} / 5</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-white/10">
              <div className="h-full rounded-full bg-[#efbc42]" style={{ width: `${((scores[key] ?? 0) / 5) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
      <div className="mt-5">
        <PartialStars label={label} value={overall} />
      </div>
    </article>
  );
}
