import Link from "next/link";
import { Suspense } from "react";
import { ArrowLeft } from "lucide-react";

import { StoryExperience } from "@/components/StoryExperience";


export default function Stories() {
  return (
    <main className="page-shell min-h-screen py-8 md:py-12">
      <div className="container-page">
        <Link
          aria-label="Back to home"
          className="panel inline-flex p-3 text-slate-300 hover:text-white"
          href="/"
        >
          <ArrowLeft size={20} />
        </Link>
        <header className="text-center">
          <p className="section-kicker mt-5">BLIND COMPARISON</p>
          <h1 className="mt-2 text-2xl font-bold uppercase tracking-wide">
            Story Comparison
          </h1>
          <div className="title-line" />
          <p className="mx-auto mt-5 max-w-xl text-sm text-slate-300">
            Generate the data-backed agentic story, then compare it with the
            human-written story.
          </p>
        </header>

        <Suspense
          fallback={
            <div className="panel mt-8 p-6 text-center text-sm text-slate-400">
              Loading story workspace...
            </div>
          }
        >
          <StoryExperience />
        </Suspense>
      </div>
    </main>
  );
}
