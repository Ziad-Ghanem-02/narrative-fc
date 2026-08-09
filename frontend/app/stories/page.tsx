import Link from "next/link";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { ContinentChart, GapChart, SemisChart, UpsetChart } from "@/components/Charts";

const storyA = [
  "For decades, World Cup football was dominated by a few traditional powerhouses. Between 1930 and the early 2000s, European and South American teams won almost every title.",
  "But the picture is changing. Underdog teams are reaching the knockout stages more often than ever before.",
  "In 2014, Costa Rica stunned the world by reaching the quarter-finals. Four years later, Croatia went all the way to the final.",
  "The 2022 World Cup saw Morocco become the first African team to reach the semi-finals, eliminating Belgium, Spain and Portugal along the way.",
  "The data shows a clear trend: the gap between giants and the rest is shrinking. Football is becoming more competitive, more global and more exciting."
];
const storyB = [
  "Traditional giants have long ruled the World Cup. Teams like Brazil, Germany and Italy built their legacies with consistency and experience.",
  "However, the last decade tells a different story. Teams from outside the usual elite are breaking through and achieving remarkable success.",
  "Japan and South Korea reached the last 16 in 2018, while Costa Rica reached the quarter-finals in 2014 against all odds.",
  "The biggest shock came in 2022 when Morocco defeated expectations to reach the semi-finals, becoming a symbol of a new era.",
  "These moments are not isolated. More teams are competing, winning and believing. The World Cup is no longer predictable. The rise of underdogs is real."
];
export default function Stories(){return <main className="page-shell min-h-screen py-8 md:py-12"><div className="container-page">
  <Link href="/" aria-label="Back to home" className="panel inline-flex p-3 text-slate-300 hover:text-white"><ArrowLeft size={20}/></Link>
  <header className="text-center"><p className="section-kicker mt-5">BLIND COMPARISON</p><h1 className="mt-2 text-2xl font-bold uppercase tracking-wide">Story Comparison</h1><div className="title-line"/><p className="mx-auto mt-5 max-w-xl text-sm text-slate-300">Two different stories about the same data. Which one convinces you more?</p></header>
  <section className="mt-8 grid gap-5 lg:grid-cols-2">{[storyA,storyB].map((story,index)=><article className="panel p-6 md:p-8" key={index}><h2 className="text-center text-sm font-bold uppercase tracking-[.18em] text-[#efbc42]">Story {index===0?"A":"B"}</h2><div className="mt-6 space-y-5 text-sm leading-7 text-slate-200">{story.map(p=><p key={p}>{p}</p>)}</div></article>)}</section>
  <section className="mt-14"><div className="text-center"><h2 className="text-lg font-bold uppercase tracking-wider">Explore the data behind these stories</h2><div className="title-line"/></div><div className="mt-8 grid gap-5 lg:grid-cols-2"><ContinentChart/><GapChart/><UpsetChart/><SemisChart/></div></section>
  <div className="mt-10 flex justify-end"><Link href="/evaluation" className="gold-button inline-flex items-center gap-3 px-7 py-4 text-sm">NEXT: RATE THE STORIES <ArrowRight size={18}/></Link></div>
</div></main>}
