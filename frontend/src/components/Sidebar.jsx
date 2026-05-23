import {
  AlertTriangle,
  BarChart3,
  BookOpen,
  Clock3,
  Code2,
  LayoutDashboard,
  ShieldCheck,
} from "lucide-react";

function Sidebar({ backendStatus, activeTab, setActiveTab }) {
  const connected = backendStatus === "connected";

  return (
    <aside className="sticky top-0 hidden h-screen w-72 shrink-0 border-r border-white/10 bg-slate-950/85 p-5 shadow-2xl shadow-black/30 backdrop-blur-xl lg:block">
      <div className="mb-8 flex items-center gap-3">
        <div className="rounded-2xl border border-cyan-400/30 bg-cyan-400/10 p-3 text-cyan-300 shadow-lg shadow-cyan-500/10">
          <ShieldCheck size={30} />
        </div>

        <div>
          <h1 className="text-xl font-bold tracking-tight text-white">
            ChainShield
          </h1>
          <p className="mt-1 text-xs leading-5 text-slate-400">
            Fraud & rug pull detection
          </p>
        </div>
      </div>

      <div
        className={`mb-6 rounded-2xl border p-4 ${
          connected
            ? "border-emerald-400/20 bg-emerald-400/10"
            : "border-yellow-400/20 bg-yellow-400/10"
        }`}
      >
        <div className="flex items-center gap-2">
          <span
            className={`h-2.5 w-2.5 rounded-full ${
              connected ? "bg-emerald-400" : "bg-yellow-300"
            }`}
          />
          <p
            className={`text-sm font-semibold ${
              connected ? "text-emerald-300" : "text-yellow-200"
            }`}
          >
            {connected ? "Backend Online" : "Backend Pending"}
          </p>
        </div>

        <p className="mt-2 text-xs leading-5 text-slate-400">
          API runs on port 8000 and frontend runs on port 5173.
        </p>
      </div>

      <nav className="space-y-2">
        <SidebarItem
          icon={<LayoutDashboard size={18} />}
          label="Overview"
          active={activeTab === "overview"}
          onClick={() => setActiveTab("overview")}
        />

        <SidebarItem
          icon={<BarChart3 size={18} />}
          label="Detailed Analysis"
          active={activeTab === "details"}
          onClick={() => setActiveTab("details")}
        />

        <SidebarItem
          icon={<AlertTriangle size={18} />}
          label="Warnings"
          active={activeTab === "warnings"}
          onClick={() => setActiveTab("warnings")}
        />

        <SidebarItem
          icon={<Clock3 size={18} />}
          label="Scan History"
          active={activeTab === "history"}
          onClick={() => setActiveTab("history")}
        />

        <SidebarItem icon={<BookOpen size={18} />} label="Learn Mode" muted />
        <SidebarItem icon={<Code2 size={18} />} label="GitHub Ready" muted />
      </nav>

      <div className="absolute bottom-5 left-5 right-5 rounded-2xl border border-cyan-400/20 bg-cyan-400/5 p-4">
        <p className="text-sm font-semibold text-cyan-200">Design Goal</p>
        <p className="mt-2 text-xs leading-5 text-slate-400">
          Clean, beginner-friendly, portfolio-quality security dashboard.
        </p>
      </div>
    </aside>
  );
}

function SidebarItem({ icon, label, active, muted, onClick }) {
  return (
    <button
      onClick={onClick}
      disabled={muted}
      className={`flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm transition ${
        active
          ? "bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-400/20"
          : muted
          ? "cursor-not-allowed text-slate-600"
          : "text-slate-400 hover:bg-white/5 hover:text-white"
      }`}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}

export default Sidebar;