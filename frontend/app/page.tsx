import Link from "next/link";
import { ArrowRight, ChartNoAxesCombined, Earth, Trophy, Users, Waves } from "lucide-react";
import WorldCupMap from "@/components/WorldCupMap";

const stats = [
  ["92", "Years of World Cups", "1930–2022", Trophy], ["22", "Tournaments", "Men's editions", Waves],
  ["1,000+", "Matches", "All stages", ChartNoAxesCombined], ["200+", "Teams", "From six continents", Users]
] as const;
const ideas = [
  [ChartNoAxesCombined, "The gap is shrinking", "Underdogs are reaching knockout stages more often than ever before."],
  [Earth, "New heroes emerge", "Teams once seen as outsiders are now making history."],
  [Trophy, "A more competitive era", "Closer matches, surprise wins and unforgettable moments."],
  [Users, "A global game", "Football's growth is creating new powerhouses worldwide."]
] as const;

export default function Home(){return <main className="page-shell">
  <section className="stadium-bg min-h-[680px] border-b border-white/10">
    <div className="container-page relative z-10 flex min-h-[680px] items-center py-16">
      <div className="grid w-full items-center gap-10 lg:grid-cols-[1.15fr_.85fr]">
        <div><div className="mb-6 flex items-center gap-2 text-xs font-bold tracking-[.18em]"><Trophy size={18} className="text-[#efbc42]"/> RISE OF UNDERDOGS</div>
          <p className="section-kicker">WORLD CUP DATA STORYTELLING</p>
          <h1 className="mt-4 text-5xl font-black uppercase leading-[.96] sm:text-6xl lg:text-7xl">The Rise of<br/><span className="text-[#efbc42]">Underdogs</span></h1>
          <h2 className="mt-5 max-w-xl text-xl font-medium">Has international football finally become more competitive?</h2>
          <p className="mt-4 max-w-xl text-sm leading-7 text-slate-300">Explore 92 years of World Cup history to see how the gap between traditional giants and emerging teams is shrinking.</p>
          <Link href="/stories" className="gold-button mt-7 inline-flex items-center gap-3 px-6 py-4 text-sm">START THE STORY <ArrowRight size={18}/></Link>
        </div>
        <div className="relative hidden min-h-[390px] items-end justify-center lg:flex"><div className="trophy absolute right-[16%] top-0"/><div className="football absolute bottom-0 left-[12%]"/></div>
      </div>
    </div>
  </section>
  <section className="container-page -mt-12 relative z-20">
    <div className="panel grid overflow-hidden sm:grid-cols-2 lg:grid-cols-4">{stats.map(([value,label,sub,Icon],i)=><div key={label} className={`p-6 text-center ${i?"border-t border-white/10 sm:border-l sm:border-t-0":""}`}><Icon className="mx-auto text-[#efbc42]" size={24}/><div className="mt-2 text-3xl font-black">{value}</div><div className="mt-1 text-xs font-bold uppercase">{label}</div><div className="mt-2 text-[11px] text-slate-400">{sub}</div></div>)}</div>
  </section>
  <section className="container-page py-20"><div className="text-center"><h2 className="text-xl font-bold uppercase tracking-wider">Football is changing</h2><div className="title-line"/></div>
    <div className="mt-9 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{ideas.map(([Icon,title,text])=><article className="panel p-6 text-center" key={title}><Icon className="mx-auto text-[#72c463]" size={34}/><h3 className="mt-4 text-sm font-bold">{title}</h3><p className="mt-3 text-xs leading-6 text-slate-400">{text}</p></article>)}</div>
  </section>
  <section className="container-page pb-20"><WorldCupMap/><p className="mx-auto mt-10 max-w-2xl text-center text-xl italic leading-8 text-slate-300">Football is no longer just a game of giants.<br/>It is a stage for anyone who dares to dream.</p><div className="title-line"/></section>
</main>}
