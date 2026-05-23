import { CheckCircle2, Copy, Database, ShieldAlert } from "lucide-react";
import { formatNumber, shortAddress, copyToClipboard } from "../utils/formatters";
import { getRiskTheme } from "../utils/riskHelpers";

function RiskSummary({ report, loading }) {
  const theme = getRiskTheme(report.riskLevel);
  const score = Math.min(Number(report.riskScore || 0), 100);

  return (
    <section className="rounded-3xl border border-white/10 bg-slate-950/75 p-5 shadow-xl shadow-black/25 backdrop-blur">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-white">Risk Summary</h2>
          <p className="mt-1 text-sm text-slate-400">
            A clear snapshot of token safety based on backend risk signals.
          </p>
        </div>

        <span className={`rounded-full border px-4 py-2 text-xs font-semibold ${theme.badge}`}>
          {loading ? "Updating..." : `${theme.label} Risk`}
        </span>
      </div>

      <div className="grid gap-5 xl:grid-cols-[0.75fr_1fr_0.75fr]">
        <div className="rounded-3xl border border-white/10 bg-black/25 p-6 text-center">
          <div
            className="mx-auto grid h-48 w-48 place-items-center rounded-full p-4"
            style={{
              background: `conic-gradient(${theme.hex} ${score * 3.6}deg, #1e293b 0deg)`,
            }}
          >
            <div className="grid h-full w-full place-items-center rounded-full bg-slate-950">
              <div>
                <p className="text-5xl font-black text-white">{score}</p>
                <p className="mt-1 text-sm text-slate-500">out of 100</p>
              </div>
            </div>
          </div>

          <p className={`mt-5 text-2xl font-bold ${theme.strongText}`}>
            {theme.label} Risk
          </p>

          <p className="mx-auto mt-2 max-w-xs text-sm leading-6 text-slate-400">
            Higher score means stronger fraud or rug-pull indicators.
          </p>
        </div>

        <div className="rounded-3xl border border-white/10 bg-black/20 p-5">
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">
            Token Identity
          </h3>

          <div className="grid gap-4 sm:grid-cols-2">
            <InfoItem label="Token Name" value={report.token.name} />
            <InfoItem label="Symbol" value={report.token.symbol} />
            <InfoItem label="Address" value={shortAddress(report.token.address, 8, 8)} copyText={report.token.address} />
            <InfoItem label="Blockchain" value="Ethereum" />
            <InfoItem label="Decimals" value={report.token.decimals} />
            <InfoItem
              label="Total Supply"
              value={formatNumber(report.token.totalSupply)}
            />
          </div>
        </div>

        <div className={`rounded-3xl border p-5 ${theme.border} ${theme.soft}`}>
          <div className="flex items-center gap-3">
            <div className="rounded-2xl border border-white/10 bg-black/20 p-3">
              <ShieldAlert size={26} className={theme.strongText} />
            </div>

            <div>
              <p className="text-sm text-slate-400">Final Level</p>
              <p className={`text-3xl font-black ${theme.strongText}`}>
                {theme.label}
              </p>
            </div>
          </div>

          <p className="mt-5 text-sm leading-6 text-slate-300">
            This report combines contract behavior, liquidity, holders, events,
            honeypot indicators, and deployer information.
          </p>

          <div className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
              Verdict
            </p>
            <p className="mt-2 text-sm leading-6 text-slate-200">
              {score >= 50
                ? "Proceed carefully. Multiple warning signals are present."
                : "No severe risk detected from available signals."}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

function InfoItem({ label, value, copyText }) {
  async function handleCopy() {
    if (copyText) await copyToClipboard(copyText);
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
      <p className="mb-2 flex items-center gap-2 text-xs text-slate-500">
        <Database size={13} />
        {label}
      </p>

      <p className="flex items-center gap-2 break-all text-sm font-semibold text-slate-100">
        {value || "Not available"}

        {copyText && (
          <button
            onClick={handleCopy}
            className="rounded-lg p-1 text-slate-500 transition hover:bg-white/10 hover:text-cyan-300"
            title="Copy"
          >
            <Copy size={14} />
          </button>
        )}

        {label === "Contract Verified" && value === "Yes" && (
          <CheckCircle2 size={14} className="text-emerald-400" />
        )}
      </p>
    </div>
  );
}

export default RiskSummary;