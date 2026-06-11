import { useQuery } from "@tanstack/react-query";

import { studioApi } from "../../api/client";

function repoLabel(repoRoot: string): string {
  const parts = repoRoot.replace(/\\/g, "/").split("/").filter(Boolean);
  return parts[parts.length - 1] ?? repoRoot;
}

function cursorWorkspaceUrl(repoRoot: string): string {
  const normalized = repoRoot.replace(/\\/g, "/");
  return `cursor://file${normalized.startsWith("/") ? normalized : `/${normalized}`}`;
}

function gateChip(gate: { gate_status?: string; card?: string; stage?: string } | null | undefined) {
  if (!gate?.gate_status) {
    return { label: "No gate file", tone: "muted" as const };
  }
  const open = gate.gate_status === "open";
  const card = gate.card ? ` · ${gate.card}` : "";
  return {
    label: `${open ? "Gate open" : "Gate closed"}${card}`,
    tone: open ? ("open" as const) : ("closed" as const),
  };
}

const toneClass = {
  open: "bg-emerald-500/20 text-emerald-300 ring-emerald-500/40",
  closed: "bg-slate-700/80 text-slate-300 ring-slate-600",
  muted: "bg-slate-800 text-slate-400 ring-slate-700",
};

export function TopBar({
  onMenuToggle,
  sidebarCollapsed = false,
}: {
  onMenuToggle: () => void;
  sidebarCollapsed?: boolean;
}) {
  const health = useQuery({ queryKey: ["studio", "health"], queryFn: studioApi.health });
  const gate = useQuery({ queryKey: ["studio", "session", "gate"], queryFn: studioApi.sessionGate });

  const repoRoot = health.data?.repo_root ?? "";
  const chip = gateChip(gate.data?.gate);
  const cursorHref = repoRoot ? cursorWorkspaceUrl(repoRoot) : undefined;

  return (
    <header className="flex h-14 shrink-0 items-center gap-3 border-b border-slate-800 bg-slate-950/90 px-4 backdrop-blur">
      <button
        type="button"
        onClick={onMenuToggle}
        data-testid="topbar-menu-toggle"
        className="rounded-lg p-2 text-slate-300 hover:bg-slate-800 hover:text-white"
        aria-label={sidebarCollapsed ? "Expand navigation" : "Toggle navigation"}
      >
        <span className="flex h-5 w-5 flex-col items-center justify-center gap-1">
          <span className="block h-0.5 w-5 bg-current" />
          <span className="block h-0.5 w-5 bg-current" />
          <span className="block h-0.5 w-5 bg-current" />
        </span>
      </button>
      <div className="min-w-0 flex-1">
        <p className="text-xs uppercase tracking-[0.15em] text-studio-accent">SDLC Studio</p>
        <p className="truncate text-sm font-semibold text-white" title={repoRoot}>
          {health.isLoading ? "Loading repo…" : repoLabel(repoRoot) || "—"}
        </p>
      </div>
      <span
        className={[
          "hidden shrink-0 rounded-full px-3 py-1 text-xs font-medium ring-1 sm:inline",
          toneClass[chip.tone],
        ].join(" ")}
        title={gate.data?.path}
      >
        {gate.isLoading ? "Gate…" : chip.label}
      </span>
      {cursorHref ? (
        <a
          href={cursorHref}
          className="shrink-0 rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-200 hover:border-studio-accent/50 hover:text-studio-accent"
        >
          Open in Cursor
        </a>
      ) : null}
    </header>
  );
}
