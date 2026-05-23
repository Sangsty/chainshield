import { useState } from "react";
import { AlertTriangle, ChevronDown, ChevronRight, Flag } from "lucide-react";

function RedFlags({ explanations = [], expandedDefault = false }) {
  const [expanded, setExpanded] = useState(expandedDefault);

  const warnings = Array.isArray(explanations) ? explanations : [];
  const visibleWarnings = expanded ? warnings : warnings.slice(0, 4);

  return (
    <section className="rounded-3xl border border-red-400/10 bg-gradient-to-br from-red-950/20 via-slate-950/80 to-slate-950/80 p-5 shadow-xl shadow-black/25 backdrop-blur">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl border border-red-400/25 bg-red-400/10 p-3 text-red-300">
            <Flag size={22} />
          </div>

          <div>
            <h2 className="text-xl font-bold text-white">Red Flags</h2>
            <p className="mt-1 text-sm text-slate-400">
              Plain-English warnings generated from backend signals.
            </p>
          </div>
        </div>

        {warnings.length > 4 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="inline-flex items-center gap-2 rounded-2xl border border-red-400/20 bg-red-400/10 px-4 py-2 text-xs text-red-200 transition hover:bg-red-400/20"
          >
            {expanded ? "Show less" : "View all"}
            <ChevronDown
              size={15}
              className={`transition ${expanded ? "rotate-180" : ""}`}
            />
          </button>
        )}
      </div>

      {warnings.length > 0 ? (
        <div className="space-y-3">
          {visibleWarnings.map((warning, index) => (
            <div
              key={`${warning}-${index}`}
              className="group flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-black/20 px-4 py-3 transition hover:border-red-400/30 hover:bg-red-400/5"
            >
              <div className="flex items-start gap-3">
                <span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-red-400 shadow-lg shadow-red-400/40" />
                <p className="text-sm leading-6 text-slate-200">{warning}</p>
              </div>

              <ChevronRight
                size={16}
                className="shrink-0 text-slate-600 transition group-hover:text-red-300"
              />
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-5">
          <p className="text-sm font-semibold text-emerald-200">
            No major red flags detected.
          </p>
          <p className="mt-2 text-sm leading-6 text-emerald-100/80">
            The backend did not return serious warning notes for this scan.
          </p>
        </div>
      )}

      <div className="mt-5 flex items-start gap-3 rounded-2xl border border-yellow-400/20 bg-yellow-400/10 p-4">
        <AlertTriangle size={18} className="mt-0.5 shrink-0 text-yellow-300" />
        <p className="text-sm leading-6 text-yellow-100/90">
          ChainShield is a decision-support tool, not a guarantee. Always verify
          contracts, liquidity, holders, and deployer history manually.
        </p>
      </div>
    </section>
  );
}

export default RedFlags;