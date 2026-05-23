import { useState } from "react";
import {
  Activity,
  Bug,
  ChevronDown,
  Droplets,
  ShieldAlert,
  UserRound,
  UsersRound,
} from "lucide-react";
import { formatPercent, shortAddress } from "../utils/formatters";
import { getRiskTheme } from "../utils/riskHelpers";

function DetailedAnalysis({ report }) {
  const [openSection, setOpenSection] = useState("Contract Analysis");

  const sections = [
    {
      title: "Contract Analysis",
      icon: ShieldAlert,
      score: report.categoryBreakdown.contract_risk,
      summary:
        "Checks risky owner permissions, verification, proxy usage, and dangerous functions.",
      content: <ContractAnalysis report={report} />,
    },
    {
      title: "Holder Analysis",
      icon: UsersRound,
      score: report.categoryBreakdown.holder_risk,
      summary:
        "Checks whether supply is concentrated among a small number of wallets.",
      content: <HolderAnalysis report={report} />,
    },
    {
      title: "Liquidity Analysis",
      icon: Droplets,
      score: report.categoryBreakdown.liquidity_risk,
      summary:
        "Reviews liquidity lock status and liquidity-related rug pull signals.",
      content: <LiquidityAnalysis report={report} />,
    },
    {
      title: "Event Log Analysis",
      icon: Activity,
      score: report.categoryBreakdown.event_risk,
      summary:
        "Looks for suspicious on-chain events such as minting and burning.",
      content: <EventAnalysis report={report} />,
    },
    {
      title: "Honeypot Analysis",
      icon: Bug,
      score: report.categoryBreakdown.honeypot_risk,
      summary:
        "Checks transfer restrictions and signs that users may not be able to sell.",
      content: <HoneypotAnalysis report={report} />,
    },
    {
      title: "Creator / Deployer Analysis",
      icon: UserRound,
      score: report.categoryBreakdown.creator_risk,
      summary:
        "Reviews creator wallet information and deployment transaction details.",
      content: <CreatorAnalysis report={report} />,
    },
  ];

  return (
    <section className="rounded-3xl border border-white/10 bg-slate-950/75 p-5 shadow-xl shadow-black/25 backdrop-blur">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-white">Detailed Analysis</h2>
          <p className="mt-1 text-sm text-slate-400">
            Expand a section to understand how each backend module contributes
            to the final risk report.
          </p>
        </div>

        <button
          onClick={() => setOpenSection(openSection ? null : "Contract Analysis")}
          className="rounded-2xl border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-300 transition hover:bg-white/10"
        >
          {openSection ? "Collapse" : "Open first"}
        </button>
      </div>

      <div className="space-y-3">
        {sections.map((section) => {
          const Icon = section.icon;
          const theme = getRiskTheme(Number(section.score || 0));
          const active = openSection === section.title;

          return (
            <article
              key={section.title}
              className={`overflow-hidden rounded-3xl border bg-black/20 transition ${
                active ? "border-cyan-400/25" : "border-white/10"
              }`}
            >
              <button
                onClick={() => setOpenSection(active ? null : section.title)}
                className="flex w-full flex-col gap-4 px-5 py-4 text-left transition hover:bg-white/[0.03] lg:flex-row lg:items-center lg:justify-between"
              >
                <div className="flex items-start gap-4">
                  <div className={`rounded-2xl border p-3 ${theme.border} ${theme.soft}`}>
                    <Icon size={22} className={theme.strongText} />
                  </div>

                  <div>
                    <h3 className="font-bold text-white">{section.title}</h3>
                    <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-400">
                      {section.summary}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${theme.badge}`}>
                    {section.score || 0}/100
                  </span>

                  <ChevronDown
                    size={18}
                    className={`text-slate-400 transition ${
                      active ? "rotate-180" : ""
                    }`}
                  />
                </div>
              </button>

              {active && (
                <div className="border-t border-white/10 p-5">
                  {section.content}
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}

function ContractAnalysis({ report }) {
  const functions = report.contract.dangerousFunctions || [];

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Detail label="Contract Verified" value={report.contract.verified ? "Yes" : "No"} />
      <Detail label="Compiler Version" value={report.contract.compilerVersion} />
      <Detail label="Proxy Contract" value={report.contract.isProxy ? "Yes" : "No"} />
      <Detail
        label="Implementation Address"
        value={report.contract.implementationAddress || "Not detected"}
      />

      <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 md:col-span-2">
        <p className="mb-3 text-sm font-semibold text-slate-200">
          Dangerous Functions Found
        </p>

        {functions.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {functions.map((item) => (
              <span
                key={item}
                className="rounded-full border border-red-400/25 bg-red-400/10 px-3 py-1 text-xs text-red-200"
              >
                {item}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-400">
            No dangerous functions were returned by the backend.
          </p>
        )}
      </div>
    </div>
  );
}

function HolderAnalysis({ report }) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Detail
        label="Top 10 Holder Percentage"
        value={formatPercent(report.holder.top10Percentage)}
      />
      <Detail label="Holder Count" value={report.holder.holderCount} />
    </div>
  );
}

function LiquidityAnalysis({ report }) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Detail
        label="Liquidity Locked"
        value={report.liquidity.locked ? "Yes" : "No / Unknown"}
      />
      <Detail label="Liquidity Risk" value={`${report.liquidity.risk}/100`} />
    </div>
  );
}

function EventAnalysis({ report }) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <Detail label="Mint Events" value={report.events.mintEvents} />
      <Detail label="Burn Events" value={report.events.burnEvents} />
      <Detail
        label="Suspicious Events"
        value={report.events.suspiciousEvents?.length || 0}
      />
    </div>
  );
}

function HoneypotAnalysis({ report }) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Detail label="Honeypot Risk" value={`${report.honeypot.risk}/100`} />
      <Detail
        label="Transfer Restrictions"
        value={report.honeypot.transferRestrictions ? "Detected" : "Not detected"}
      />
    </div>
  );
}

function CreatorAnalysis({ report }) {
  return (
    <div className="grid gap-4">
      <Detail
        label="Creator Address"
        value={shortAddress(report.creator.address, 12, 12)}
      />
      <Detail
        label="Creation Transaction Hash"
        value={shortAddress(report.creator.creationTxHash, 12, 12)}
      />
    </div>
  );
}

function Detail({ label, value }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
      <p className="mb-2 text-xs uppercase tracking-[0.18em] text-slate-500">
        {label}
      </p>
      <p className="break-all text-sm font-semibold text-slate-100">
        {value ?? "Not available"}
      </p>
    </div>
  );
}

export default DetailedAnalysis;