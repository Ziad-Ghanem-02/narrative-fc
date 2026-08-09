"use client";
import Link from "next/link";
import { useState } from "react";
import { ArrowLeft, BarChart3, Heart, Lightbulb, ShieldCheck, Star } from "lucide-react";

const criteria = [
  ["Clarity","How easy is the story to understand?",Lightbulb], ["Trustworthiness","How much do you trust the claims made?",ShieldCheck],
  ["Use of evidence","How well does the story use data and facts?",BarChart3], ["Insightfulness","How insightful and surprising is the story?",Lightbulb],
  ["Engagement","How engaging and interesting is it?",Heart]
] as const;
function Stars({value,onChange}:{value:number,onChange:(n:number)=>void}){return <div className="flex justify-center gap-1">{[1,2,3,4,5].map(n=><button aria-label={`${n} stars`} key={n} onClick={()=>onChange(n)}><Star size={25} className={n<=value?"fill-[#efbc42] text-[#efbc42]":"text-slate-600"}/></button>)}</div>}
export default function Evaluation(){const [a,setA]=useState<number[]>([0,0,0,0,0]);const[b,setB]=useState<number[]>([0,0,0,0,0]);const[done,setDone]=useState(false);return <main className="page-shell min-h-screen py-8 md:py-12"><div className="container-page">
  <Link href="/stories" className="panel inline-flex p-3 text-slate-300"><ArrowLeft size={20}/></Link>
  <header className="text-center"><p className="section-kicker mt-5">HUMAN EVALUATION</p><h1 className="mt-2 text-2xl font-bold uppercase tracking-wide">Rate the Stories</h1><div className="title-line"/><p className="mx-auto mt-5 max-w-xl text-sm text-slate-300">Evaluate both stories using the same criteria. There are no right or wrong answers.</p></header>
  <section className="panel mt-8 overflow-hidden"><div className="grid grid-cols-[1fr_1.15fr_1fr] border-b border-white/10 p-5 text-center text-sm font-bold"><span>STORY A</span><span className="text-slate-400">EVALUATION CRITERIA</span><span>STORY B</span></div>{criteria.map(([title,desc,Icon],i)=><div key={title} className="grid grid-cols-1 items-center gap-5 border-b border-white/10 p-6 text-center md:grid-cols-[1fr_1.15fr_1fr]"><div className="order-2 md:order-1"><p className="mb-2 text-xs text-slate-400 md:hidden">Story A</p><Stars value={a[i]} onChange={n=>setA(x=>x.map((v,j)=>j===i?n:v))}/></div><div className="order-1 md:order-2"><Icon className="mx-auto text-[#efbc42]" size={27}/><h3 className="mt-2 text-sm font-bold">{title}</h3><p className="mt-1 text-xs text-slate-400">{desc}</p></div><div className="order-3"><p className="mb-2 text-xs text-slate-400 md:hidden">Story B</p><Stars value={b[i]} onChange={n=>setB(x=>x.map((v,j)=>j===i?n:v))}/></div></div>)}</section>
  <section className="panel mt-5 p-6"><label className="text-sm font-medium">Which story did you prefer overall and why?</label><textarea className="mt-3 min-h-32 w-full rounded-lg border border-white/10 bg-[#07131c] p-4 text-sm outline-none focus:border-[#efbc42]" placeholder="Write your thoughts here..."/><button onClick={()=>setDone(true)} className="gold-button mt-4 w-full py-4 text-sm">SUBMIT MY RATINGS</button>{done&&<p className="mt-4 text-center text-sm text-[#71d16d]">Thank you — your evaluation has been recorded for this prototype.</p>}</section>
  <section className="mt-6 flex gap-4 rounded-xl border border-white/10 bg-white/[.025] p-6"><ShieldCheck className="shrink-0 text-slate-300"/><div><h2 className="text-sm font-bold uppercase">Why your feedback matters</h2><p className="mt-2 text-xs leading-6 text-slate-400">Your ratings help compare how readers perceive different storytelling approaches without revealing the author type beforehand.</p></div></section>
</div></main>}
