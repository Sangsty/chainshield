import { LockKeyhole, Radar, ShieldCheck } from "lucide-react";

function HeroSection() {
  return (
    <section className="overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900/95 via-slate-950 to-cyan-950/30 p-6 shadow-2xl shadow-black/30 lg:p-8">
      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div>
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-xs font-medium text-cyan-200">
            <ShieldCheck size={15} />
            Explainable token security intelligence
          </div>

          <h1 className="max-w-3xl text-4xl font-black tracking-tight text-white sm:text-5xl lg:text-6xl">
            Scan tokens.
            <span className="block">
              Spot <span className="text-cyan-300">risk</span> before trust.
            </span>
          </h1>

          <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">
            ChainShield converts raw blockchain data into a simple risk score,
            red flags, and readable explanations for fraud and rug pull signals.
          </p>

          <div className="mt-6 grid gap-3 sm:grid-cols-3">
            <MiniStat icon={<Radar size={17} />} label="50+ Signals" />
            <MiniStat icon={<LockKeyhole size={17} />} label="Risk Scoring" />
            <MiniStat icon={<ShieldCheck size={17} />} label="Explainable UI" />
          </div>
        </div>

        <div className="relative hidden min-h-72 items-center justify-center lg:flex">
          <div className="absolute h-72 w-72 rounded-full border border-cyan-400/10" />
          <div className="absolute h-52 w-52 rounded-full border border-cyan-400/15" />
          <div className="absolute h-32 w-32 rounded-full border border-cyan-400/20" />

          <div className="relative rounded-[2rem] border border-cyan-400/30 bg-cyan-400/10 p-8 text-cyan-200 shadow-2xl shadow-cyan-500/20">
            <ShieldCheck size={96} strokeWidth={1.4} />
          </div>

          <div className="absolute bottom-5 rounded-full border border-white/10 bg-slate-950/80 px-4 py-2 text-xs text-slate-300">
            Live backend report ready
          </div>
        </div>
      </div>
    </section>
  );
}

function MiniStat({ icon, label }) {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-slate-200">
      <span className="text-cyan-300">{icon}</span>
      {label}
    </div>
  );
}

export default HeroSection;