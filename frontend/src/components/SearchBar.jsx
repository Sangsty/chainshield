import { Loader2, Search, Sparkles } from "lucide-react";

const EXAMPLES = [
  {
    label: "USDT",
    address: "0xdAC17F958D2ee523a2206206994597C13D831ec7",
  },
  {
    label: "USDC",
    address: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
  },
  {
    label: "DAI",
    address: "0x6B175474E89094C44Da98b954EedeAC495271d0F",
  },
  {
    label: "Suspicious sample",
    address: "0x000000000000000000000000000000000000dead",
    danger: true,
  },
];

function SearchBar({
  address,
  setAddress,
  onScan,
  onExample,
  loading,
  error,
}) {
  return (
    <section className="rounded-3xl border border-white/10 bg-slate-950/75 p-5 shadow-xl shadow-black/25 backdrop-blur">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-white">Token Scanner</h2>
          <p className="mt-1 text-sm text-slate-400">
            Enter any Ethereum token contract address to generate a report.
          </p>
        </div>

        <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-xs text-cyan-200">
          <Sparkles size={14} />
          Interactive Phase 4 UI
        </div>
      </div>

      <div className="flex flex-col gap-3 lg:flex-row">
        <div className="relative flex-1">
          <Search
            size={18}
            className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
          />

          <input
            value={address}
            onChange={(event) => setAddress(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") onScan();
            }}
            placeholder="Paste token contract address, e.g. 0xdAC17F..."
            className="w-full rounded-2xl border border-white/10 bg-black/30 py-4 pl-12 pr-4 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-400/60 focus:ring-4 focus:ring-cyan-400/10"
          />
        </div>

        <button
          onClick={() => onScan()}
          disabled={loading}
          className="inline-flex min-w-40 items-center justify-center gap-2 rounded-2xl bg-cyan-400 px-6 py-4 text-sm font-bold text-slate-950 transition hover:-translate-y-0.5 hover:bg-cyan-300 hover:shadow-lg hover:shadow-cyan-400/20 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {loading ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              Scanning
            </>
          ) : (
            <>
              <Search size={18} />
              Scan Token
            </>
          )}
        </button>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2 text-xs">
        <span className="text-slate-500">Quick examples:</span>

        {EXAMPLES.map((example) => (
          <button
            key={example.address}
            onClick={() => onExample(example.address)}
            className={`rounded-full border px-4 py-2 transition ${
              example.danger
                ? "border-red-400/25 bg-red-400/10 text-red-200 hover:bg-red-400/20"
                : "border-cyan-400/25 bg-cyan-400/10 text-cyan-200 hover:bg-cyan-400/20"
            }`}
          >
            {example.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="mt-4 rounded-2xl border border-red-400/25 bg-red-500/10 px-4 py-3 text-sm leading-6 text-red-100">
          {error}
        </div>
      )}
    </section>
  );
}

export default SearchBar;