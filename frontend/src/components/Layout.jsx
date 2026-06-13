import { useEffect, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  Braces,
  Clock3,
  LayoutDashboard,
  ShieldCheck,
} from "lucide-react";
import Sidebar from "./Sidebar";
import HeroSection from "./HeroSection";
import SearchBar from "./SearchBar";
import RiskSummary from "./RiskSummary";
import RiskBreakdown from "./RiskBreakdown";
import RedFlags from "./RedFlags";
import TokenOverview from "./TokenOverview";
import DetailedAnalysis from "./DetailedAnalysis";
import { checkBackendHealth, inspectToken } from "../services/api";
import { normalizeReport } from "../utils/riskHelpers";
import MLPredictionCard from "./MLPredictionCard";

function Layout() {
  const [address, setAddress] = useState("");
  const [report, setReport] = useState(null);
  const [scanHistory, setScanHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [backendStatus, setBackendStatus] = useState("checking");
  const [activeTab, setActiveTab] = useState("overview");
  const [showRawJson, setShowRawJson] = useState(false);

  useEffect(() => {
    async function checkHealth() {
      try {
        await checkBackendHealth();
        setBackendStatus("connected");
      } catch {
        setBackendStatus("offline");
      }
    }

    checkHealth();
  }, []);

  async function handleScan(customAddress) {
    const finalAddress = customAddress || address;

    if (!finalAddress.trim()) {
      setError("Please enter a token contract address first.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setShowRawJson(false);
      setActiveTab("overview");

      const data = await inspectToken(finalAddress);
      const normalized = normalizeReport(data);

      setReport(normalized);

      const historyItem = {
        id: `${normalized.token.address}-${Date.now()}`,
        name: normalized.token.name,
        symbol: normalized.token.symbol,
        address: normalized.token.address || finalAddress,
        score: normalized.riskScore,
        level: normalized.riskLevel,
        scannedAt: new Date().toLocaleString(),
      };

      setScanHistory((previous) => {
        const filtered = previous.filter(
          (item) =>
            item.address.toLowerCase() !== historyItem.address.toLowerCase()
        );

        return [historyItem, ...filtered].slice(0, 6);
      });
    } catch (err) {
      console.error(err);
      setError(
        "Scan failed. Check backend, CORS, and whether the token address is valid."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleExample(exampleAddress) {
    setAddress(exampleAddress);
    handleScan(exampleAddress);
  }

  return (
    <div className="min-h-screen text-slate-50">
      <div className="pointer-events-none fixed inset-0 opacity-80">
        <div className="absolute left-[-12rem] top-[-12rem] h-96 w-96 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute right-[-10rem] top-1/3 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute bottom-[-12rem] left-1/3 h-96 w-96 rounded-full bg-red-500/5 blur-3xl" />
      </div>

      <div className="relative flex">
        <Sidebar
          backendStatus={backendStatus}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />

        <main className="min-h-screen flex-1 px-4 py-5 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-7xl space-y-5">
            <TopBar backendStatus={backendStatus} />

            <HeroSection />

            <SearchBar
              address={address}
              setAddress={setAddress}
              onScan={handleScan}
              onExample={handleExample}
              loading={loading}
              error={error}
            />

            {loading && <LoadingReport />}

            {!loading && !report && <EmptyScanState />}

            {!loading && report && (
              <>
                <TabBar
                  activeTab={activeTab}
                  setActiveTab={setActiveTab}
                  showRawJson={showRawJson}
                  setShowRawJson={setShowRawJson}
                />

                {activeTab === "overview" && (
                  <div className="space-y-5">
                    <RiskSummary report={report} loading={loading} />
                    <RiskBreakdown breakdown={report.categoryBreakdown} />
                    <MLPredictionCard mlPrediction={report.raw?.ml_prediction} />
                    <div className="grid gap-5 xl:grid-cols-[1fr_0.9fr]">
                      <RedFlags explanations={report.explanations} />
                      <TokenOverview report={report} />
                    </div>
                  </div>
                )}

                {activeTab === "details" && <DetailedAnalysis report={report} />}

                {activeTab === "warnings" && (
                  <div className="space-y-5">
                    <RedFlags
                      explanations={report.explanations}
                      expandedDefault
                    />
                    <RiskBreakdown breakdown={report.categoryBreakdown} />
                  </div>
                )}

                {activeTab === "history" && (
                  <ScanHistoryView
                    history={scanHistory}
                    onSelect={(item) => {
                      setAddress(item.address);
                      handleScan(item.address);
                    }}
                  />
                )}

                {showRawJson && (
                  <section className="rounded-3xl border border-white/10 bg-slate-950/80 p-5 shadow-xl shadow-black/30">
                    <div className="mb-3 flex items-center justify-between gap-3">
                      <div>
                        <h3 className="text-lg font-semibold text-white">
                          Raw Backend Response
                        </h3>
                        <p className="mt-1 text-sm text-slate-400">
                          Useful for checking whether frontend mapping is
                          correct.
                        </p>
                      </div>

                      <button
                        onClick={() => setShowRawJson(false)}
                        className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-300 transition hover:bg-white/10"
                      >
                        Hide JSON
                      </button>
                    </div>

                    <pre className="max-h-[28rem] overflow-auto rounded-2xl border border-white/10 bg-black/40 p-4 text-xs leading-6 text-cyan-100">
                      {JSON.stringify(report.raw, null, 2)}
                    </pre>
                  </section>
                )}
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

function EmptyScanState() {
  return (
    <section className="rounded-3xl border border-dashed border-cyan-400/25 bg-slate-950/50 p-8 text-center shadow-xl shadow-black/20">
      <div className="mx-auto mb-4 grid h-16 w-16 place-items-center rounded-2xl border border-cyan-400/25 bg-cyan-400/10 text-cyan-300">
        <ShieldCheck size={30} />
      </div>

      <h2 className="text-2xl font-bold text-white">No token scanned yet</h2>

      <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-slate-400">
        Enter a token contract address or choose an example. Once the scan
        completes, ChainShield will show risk score, category breakdown, red
        flags, token metadata, and detailed analysis.
      </p>
    </section>
  );
}

function LoadingReport() {
  return (
    <section className="rounded-3xl border border-cyan-400/20 bg-slate-950/70 p-8 shadow-xl shadow-black/25">
      <div className="mx-auto max-w-3xl text-center">
        <div className="mx-auto mb-5 h-14 w-14 animate-spin rounded-full border-4 border-slate-800 border-t-cyan-400" />

        <h2 className="text-2xl font-bold text-white">
          Scanning token on-chain signals...
        </h2>

        <p className="mt-3 text-sm leading-6 text-slate-400">
          ChainShield is checking contract permissions, liquidity, holder
          patterns, honeypot indicators, events, and deployer information.
        </p>

        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          <SkeletonStep label="Contract analysis" />
          <SkeletonStep label="Risk scoring" />
          <SkeletonStep label="Report generation" />
        </div>
      </div>
    </section>
  );
}

function SkeletonStep({ label }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
      <div className="mx-auto mb-3 h-2 w-20 animate-pulse rounded-full bg-cyan-400/30" />
      <p className="text-xs text-slate-400">{label}</p>
    </div>
  );
}

function ScanHistoryView({ history, onSelect }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-slate-950/75 p-5 shadow-xl shadow-black/25 backdrop-blur">
      <div className="mb-5 flex items-center gap-3">
        <div className="rounded-2xl border border-cyan-400/25 bg-cyan-400/10 p-3 text-cyan-300">
          <Clock3 size={22} />
        </div>

        <div>
          <h2 className="text-xl font-bold text-white">Scan History</h2>
          <p className="mt-1 text-sm text-slate-400">
            Recent scans from this browser session.
          </p>
        </div>
      </div>

      {history.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-white/10 bg-black/20 p-6 text-center">
          <p className="text-sm text-slate-400">
            No scan history yet. Scan USDT, USDC, or DAI to populate this
            section.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {history.map((item) => (
            <button
              key={item.id}
              onClick={() => onSelect(item)}
              className="rounded-3xl border border-white/10 bg-black/20 p-5 text-left transition hover:-translate-y-1 hover:border-cyan-400/30 hover:bg-white/[0.04]"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="text-lg font-bold text-white">
                    {item.name || "Unknown Token"}
                  </h3>
                  <p className="mt-1 text-sm text-slate-400">{item.symbol}</p>
                </div>

                <span className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs text-cyan-200">
                  {item.level}
                </span>
              </div>

              <p className="mt-4 break-all text-xs text-slate-500">
                {item.address}
              </p>

              <div className="mt-4 flex items-center justify-between">
                <p className="text-sm text-slate-400">{item.scannedAt}</p>
                <p className="text-2xl font-black text-cyan-300">
                  {item.score}
                </p>
              </div>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}

function TopBar({ backendStatus }) {
  const connected = backendStatus === "connected";

  return (
    <header className="flex flex-wrap items-center justify-between gap-4 rounded-3xl border border-white/10 bg-slate-950/70 px-5 py-4 shadow-xl shadow-black/20 backdrop-blur">
      <div className="flex items-center gap-3 lg:hidden">
        <div className="rounded-2xl border border-cyan-400/25 bg-cyan-400/10 p-3 text-cyan-300">
          <ShieldCheck size={24} />
        </div>

        <div>
          <h1 className="text-lg font-bold">ChainShield</h1>
          <p className="text-xs text-slate-400">Token risk dashboard</p>
        </div>
      </div>

      <div className="hidden lg:block">
        <p className="text-sm text-slate-400">Phase 4 Frontend Interface</p>
        <h2 className="text-xl font-semibold text-white">
          Explainable On-Chain Fraud Detection
        </h2>
      </div>

      <div
        className={`inline-flex items-center gap-2 rounded-full border px-4 py-2 text-xs font-medium ${
          connected
            ? "border-emerald-400/25 bg-emerald-400/10 text-emerald-300"
            : "border-yellow-400/25 bg-yellow-400/10 text-yellow-200"
        }`}
      >
        <span
          className={`h-2 w-2 rounded-full ${
            connected ? "bg-emerald-400" : "bg-yellow-300"
          }`}
        />
        {connected ? "Backend Connected" : "Backend Checking"}
      </div>
    </header>
  );
}

function TabBar({ activeTab, setActiveTab, showRawJson, setShowRawJson }) {
  const tabs = [
    {
      key: "overview",
      label: "Overview",
      icon: LayoutDashboard,
    },
    {
      key: "details",
      label: "Detailed Analysis",
      icon: BarChart3,
    },
    {
      key: "warnings",
      label: "Warnings",
      icon: AlertTriangle,
    },
    {
      key: "history",
      label: "Scan History",
      icon: Clock3,
    },
  ];

  return (
    <section className="flex flex-wrap items-center justify-between gap-3 rounded-3xl border border-white/10 bg-slate-950/70 p-2 shadow-xl shadow-black/20 backdrop-blur">
      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.key;

          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`inline-flex items-center gap-2 rounded-2xl px-4 py-3 text-sm font-medium transition ${
                active
                  ? "bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-400/20"
                  : "text-slate-400 hover:bg-white/5 hover:text-white"
              }`}
            >
              <Icon size={17} />
              {tab.label}
            </button>
          );
        })}
      </div>

      <button
        onClick={() => setShowRawJson(!showRawJson)}
        className={`inline-flex items-center gap-2 rounded-2xl border px-4 py-3 text-sm transition ${
          showRawJson
            ? "border-cyan-400/30 bg-cyan-400/10 text-cyan-200"
            : "border-white/10 bg-white/5 text-slate-300 hover:bg-white/10"
        }`}
      >
        <Braces size={17} />
        Raw JSON
      </button>
    </section>
  );
}

export default Layout;