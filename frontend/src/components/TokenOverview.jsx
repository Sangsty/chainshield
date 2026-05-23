import { CheckCircle2, Copy, ExternalLink, Info } from "lucide-react";
import { copyToClipboard, formatNumber, shortAddress } from "../utils/formatters";

function TokenOverview({ report }) {
  const token = report.token;
  const contract = report.contract;
  const creator = report.creator;

  return (
    <section className="rounded-3xl border border-white/10 bg-slate-950/75 p-5 shadow-xl shadow-black/25 backdrop-blur">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl border border-cyan-400/25 bg-cyan-400/10 p-3 text-cyan-300">
            <Info size={22} />
          </div>

          <div>
            <h2 className="text-xl font-bold text-white">Token Overview</h2>
            <p className="mt-1 text-sm text-slate-400">
              Metadata, contract status, and deployer details.
            </p>
          </div>
        </div>

        {token.address && (
          <a
            href={`https://etherscan.io/token/${token.address}`}
            target="_blank"
            rel="noreferrer"
            className="hidden items-center gap-2 rounded-2xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-xs text-cyan-200 transition hover:bg-cyan-400/20 sm:inline-flex"
          >
            Etherscan
            <ExternalLink size={14} />
          </a>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <OverviewCard label="Name" value={token.name} />
        <OverviewCard label="Symbol" value={token.symbol} />
        <OverviewCard label="Decimals" value={token.decimals} />
        <OverviewCard label="Total Supply" value={formatNumber(token.totalSupply)} />
        <OverviewCard
          label="Verified Contract"
          value={contract.verified ? "Yes" : "No"}
          good={contract.verified}
        />
        <OverviewCard
          label="Proxy Contract"
          value={contract.isProxy ? "Yes" : "No"}
        />
      </div>

      <div className="mt-4 rounded-3xl border border-white/10 bg-black/20 p-4">
        <p className="mb-2 text-xs uppercase tracking-[0.2em] text-slate-500">
          Creator / Deployer
        </p>

        <button
          onClick={() => copyToClipboard(creator.address)}
          className="flex w-full items-center justify-between gap-3 rounded-2xl bg-white/[0.03] px-4 py-3 text-left text-sm text-slate-200 transition hover:bg-white/[0.06]"
        >
          <span className="break-all">{shortAddress(creator.address, 10, 10)}</span>
          <Copy size={15} className="shrink-0 text-slate-500" />
        </button>

        <p className="mt-3 text-xs leading-5 text-slate-500">
          Creator wallet is useful for deployer tracking and repeat scam
          detection.
        </p>
      </div>
    </section>
  );
}

function OverviewCard({ label, value, good }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
      <p className="mb-2 text-xs text-slate-500">{label}</p>
      <p className="flex items-center gap-2 break-all text-sm font-semibold text-slate-100">
        {good && <CheckCircle2 size={15} className="text-emerald-400" />}
        {value ?? "Not available"}
      </p>
    </div>
  );
}

export default TokenOverview;