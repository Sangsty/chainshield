import { Brain, ShieldCheck, ShieldX, AlertTriangle } from "lucide-react";

// ── Helpers ───────────────────────────────────────────────────────────────────
function getPredictionTheme(prediction) {
  switch (prediction) {
    case "safe":
      return {
        label      : "Safe",
        icon       : ShieldCheck,
        badgeBg    : "bg-emerald-400/10 border-emerald-400/25 text-emerald-300",
        barColor   : "bg-emerald-400",
        glowColor  : "shadow-emerald-500/10",
        textColor  : "text-emerald-400",
        ringColor  : "#34d399",
      };
    case "scam":
      return {
        label      : "Scam",
        icon       : ShieldX,
        badgeBg    : "bg-red-400/10 border-red-400/25 text-red-300",
        barColor   : "bg-red-400",
        glowColor  : "shadow-red-500/10",
        textColor  : "text-red-400",
        ringColor  : "#f87171",
      };
    default:
      return {
        label      : "Unknown",
        icon       : AlertTriangle,
        badgeBg    : "bg-yellow-400/10 border-yellow-400/25 text-yellow-300",
        barColor   : "bg-yellow-400",
        glowColor  : "shadow-yellow-500/10",
        textColor  : "text-yellow-400",
        ringColor  : "#fbbf24",
      };
  }
}

function getDirectionColor(direction) {
  return direction === "toward_scam"
    ? "bg-red-400"
    : "bg-emerald-400";
}

function getDirectionLabel(direction) {
  return direction === "toward_scam"
    ? "↑ Scam Signal"
    : "↓ Safe Signal";
}

function getDirectionTextColor(direction) {
  return direction === "toward_scam"
    ? "text-red-400"
    : "text-emerald-400";
}

// ── Confidence Ring ───────────────────────────────────────────────────────────
function ConfidenceRing({ confidence, ringColor }) {
  const pct   = Math.round(confidence * 100);
  const deg   = pct * 3.6;
  return (
    <div
      className="mx-auto grid h-36 w-36 place-items-center rounded-full p-3"
      style={{
        background: `conic-gradient(${ringColor} ${deg}deg, #1e293b 0deg)`,
      }}
    >
      <div className="grid h-full w-full place-items-center rounded-full bg-slate-950">
        <div className="text-center">
          <p className="text-3xl font-black text-white">{pct}%</p>
          <p className="mt-1 text-xs text-slate-500">confidence</p>
        </div>
      </div>
    </div>
  );
}

// ── Feature Bar ───────────────────────────────────────────────────────────────
function FeatureBar({ feature }) {
  const barColor  = getDirectionColor(feature.direction);
  const textColor = getDirectionTextColor(feature.direction);
  const label     = getDirectionLabel(feature.direction);
  const pct       = Math.min(feature.importance_pct, 100);

  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
      <div className="mb-2 flex items-center justify-between gap-2">
        <p className="text-xs font-medium text-slate-200 break-all">
          {feature.feature.replace(/_/g, " ")}
        </p>
        <span className={`shrink-0 text-xs font-semibold ${textColor}`}>
          {label}
        </span>
      </div>
      <div className="mb-2 h-1.5 w-full rounded-full bg-slate-800">
        <div
          className={`h-full rounded-full ${barColor} transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="flex items-center justify-between">
        <p className="text-xs text-slate-500">
          Value: <span className="text-slate-300">{feature.value}</span>
        </p>
        <p className="text-xs text-slate-500">
          Weight: <span className="text-slate-300">{pct}%</span>
        </p>
      </div>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────
function MLPredictionCard({ mlPrediction }) {
  // If no ML data or error status
  if (!mlPrediction || mlPrediction.status === "error") {
    return (
      <section className="rounded-3xl border border-white/10 bg-slate-950/75 p-5 shadow-xl shadow-black/25 backdrop-blur">
        <div className="flex items-center gap-3 mb-4">
          <div className="rounded-2xl border border-white/10 bg-black/20 p-3 text-cyan-300">
            <Brain size={22} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">ML Prediction</h2>
            <p className="text-sm text-slate-400">
              Machine learning fraud analysis
            </p>
          </div>
        </div>
        <div className="rounded-2xl border border-dashed border-white/10 bg-black/20 p-6 text-center">
          <p className="text-sm text-slate-400">
            {mlPrediction?.message || "ML prediction unavailable for this token."}
          </p>
        </div>
      </section>
    );
  }

  const theme     = getPredictionTheme(mlPrediction.prediction);
  const Icon      = theme.icon;
  const scamPct   = Math.round((mlPrediction.scam_probability || 0) * 100);
  const safePct   = Math.round((mlPrediction.safe_probability || 0) * 100);

  return (
    <section className="rounded-3xl border border-white/10 bg-slate-950/75 p-5 shadow-xl shadow-black/25 backdrop-blur">

      {/* Header */}
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl border border-white/10 bg-black/20 p-3 text-cyan-300">
            <Brain size={22} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">ML Prediction</h2>
            <p className="mt-1 text-sm text-slate-400">
              Random Forest model · SHAP explainability
            </p>
          </div>
        </div>
        <span className={`rounded-full border px-4 py-2 text-xs font-semibold ${theme.badgeBg}`}>
          {theme.label} Detected
        </span>
      </div>

      {/* Main Grid */}
      <div className="grid gap-5 xl:grid-cols-[0.6fr_1fr]">

        {/* Left — Confidence + Probabilities */}
        <div className="rounded-3xl border border-white/10 bg-black/25 p-6 text-center space-y-5">
          <ConfidenceRing
            confidence={mlPrediction.confidence}
            ringColor={theme.ringColor}
          />

          <div className="flex items-center justify-center gap-3">
            <div className={`rounded-2xl border p-3 ${theme.badgeBg}`}>
              <Icon size={22} />
            </div>
            <div className="text-left">
              <p className="text-xs text-slate-500">Prediction</p>
              <p className={`text-2xl font-black ${theme.textColor}`}>
                {theme.label}
              </p>
            </div>
          </div>

          {/* Probability Bars */}
          <div className="space-y-3 text-left">
            <div>
              <div className="mb-1 flex justify-between text-xs text-slate-400">
                <span>Safe probability</span>
                <span className="text-emerald-400">{safePct}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-800">
                <div
                  className="h-full rounded-full bg-emerald-400 transition-all duration-500"
                  style={{ width: `${safePct}%` }}
                />
              </div>
            </div>
            <div>
              <div className="mb-1 flex justify-between text-xs text-slate-400">
                <span>Scam probability</span>
                <span className="text-red-400">{scamPct}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-800">
                <div
                  className="h-full rounded-full bg-red-400 transition-all duration-500"
                  style={{ width: `${scamPct}%` }}
                />
              </div>
            </div>
          </div>

          <p className="text-xs text-slate-600">
            {mlPrediction.model_used}
          </p>
        </div>

        {/* Right — SHAP Feature Explanations */}
        <div className="rounded-3xl border border-white/10 bg-black/20 p-5">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">
            Why this prediction?
          </h3>
          <div className="space-y-3">
            {mlPrediction.top_features?.map((feature) => (
              <FeatureBar key={feature.feature} feature={feature} />
            ))}
          </div>
          <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="text-xs text-slate-500 leading-5">
              Each bar shows how much a feature influenced the prediction.
              Green bars push toward <span className="text-emerald-400">safe</span>,
              red bars push toward <span className="text-red-400">scam</span>.
              Bar width shows relative importance.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default MLPredictionCard;