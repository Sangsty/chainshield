import {
  Activity,
  Bug,
  Droplets,
  ShieldAlert,
  UserRound,
  UsersRound,
} from "lucide-react";
import { getRiskTheme } from "../utils/riskHelpers";

const riskCategories = [
  {
    key: "contract_risk",
    title: "Contract",
    subtitle: "Code & permissions",
    icon: ShieldAlert,
  },
  {
    key: "liquidity_risk",
    title: "Liquidity",
    subtitle: "Pool & lock safety",
    icon: Droplets,
  },
  {
    key: "holder_risk",
    title: "Holders",
    subtitle: "Supply concentration",
    icon: UsersRound,
  },
  {
    key: "honeypot_risk",
    title: "Honeypot",
    subtitle: "Sell restrictions",
    icon: Bug,
  },
  {
    key: "creator_risk",
    title: "Creator",
    subtitle: "Deployer behavior",
    icon: UserRound,
  },
  {
    key: "event_risk",
    title: "Events",
    subtitle: "Mint/burn logs",
    icon: Activity,
  },
];

function RiskBreakdown({ breakdown }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-slate-950/75 p-5 shadow-xl shadow-black/25 backdrop-blur">
      <div className="mb-5">
        <h2 className="text-xl font-bold text-white">Category Breakdown</h2>
        <p className="mt-1 text-sm text-slate-400">
          See exactly which areas increased or reduced the final score.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {riskCategories.map((category) => {
          const value = Number(breakdown?.[category.key] || 0);
          const theme = getRiskTheme(value);
          const Icon = category.icon;

          return (
            <article
              key={category.key}
              className="group rounded-3xl border border-white/10 bg-black/20 p-5 transition hover:-translate-y-1 hover:border-cyan-400/30 hover:bg-white/[0.04]"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className={`rounded-2xl border p-3 ${theme.border} ${theme.soft}`}>
                    <Icon size={22} className={theme.strongText} />
                  </div>

                  <div>
                    <h3 className="font-semibold text-white">
                      {category.title}
                    </h3>
                    <p className="mt-1 text-xs text-slate-500">
                      {category.subtitle}
                    </p>
                  </div>
                </div>

                <span className={`rounded-full border px-3 py-1 text-xs ${theme.badge}`}>
                  {theme.label}
                </span>
              </div>

              <div className="mt-5 flex items-end gap-1">
                <p className={`text-4xl font-black ${theme.strongText}`}>
                  {value}
                </p>
                <p className="mb-1 text-sm text-slate-500">/100</p>
              </div>

              <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
                <div
                  className={`h-full rounded-full ${theme.progress}`}
                  style={{ width: `${Math.min(value, 100)}%` }}
                />
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}

export default RiskBreakdown;