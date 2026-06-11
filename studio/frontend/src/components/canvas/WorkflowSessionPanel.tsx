import { Link } from "react-router-dom";

import type { DashboardSummary } from "../../types/studio";

const LIVE_SOURCE_LABEL: Record<NonNullable<DashboardSummary["session"]["live_source"]>, string> = {
  gate: "session-gate.json",
  handoff: "orchestrator-handoff",
  observability: "recent observability events",
};

type WorkflowSessionPanelProps = {
  session: DashboardSummary["session"] | undefined;
  stageName?: string | null;
  activeTrackLabel?: string;
};

export function WorkflowSessionPanel({
  session,
  stageName,
  activeTrackLabel,
}: WorkflowSessionPanelProps) {
  const gateOpen = Boolean(session?.gate_open);
  const executionActive = Boolean(session?.execution_active ?? gateOpen);
  const liveSource = session?.live_source ?? (gateOpen ? "gate" : null);

  const gateLabel = gateOpen ? "Gate open" : "Gate closed";
  const gateClass = gateOpen ? "text-emerald-400" : "text-slate-400";

  return (
    <div
      data-testid="workflow-session-panel"
      className="rounded-xl border border-slate-800 bg-surface-card p-4"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Live session
          </p>
          <p className="mt-1 text-sm text-slate-300">
            {executionActive
              ? gateOpen
                ? "Gate is open — workflow steps reflect the active stage from session-gate."
                : `Work in progress (derived from ${liveSource ? LIVE_SOURCE_LABEL[liveSource] : "handoff"}) — gate is closed but routing is active.`
              : "No active execution — start a card with workflow start or wait for handoff routing."}
          </p>
        </div>
        {executionActive ? (
          <span className="inline-flex items-center gap-2 rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-300">
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
            Live
          </span>
        ) : null}
      </div>

      <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Gate</dt>
          <dd className={`mt-0.5 font-medium ${gateClass}`}>{gateLabel}</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Execution</dt>
          <dd className={`mt-0.5 font-medium ${executionActive ? "text-emerald-400" : "text-slate-400"}`}>
            {executionActive ? "Active" : "Idle"}
          </dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Card</dt>
          <dd className="mt-0.5 font-mono text-white">{session?.card?.trim() || "—"}</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Active track</dt>
          <dd className="mt-0.5 text-white">{activeTrackLabel ?? "—"}</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Stage</dt>
          <dd className="mt-0.5 text-white">
            {stageName ?? session?.stage ?? "—"}
            {session?.inferred_stage ? (
              <span className="ml-1 text-[10px] text-amber-300/90">(inferred)</span>
            ) : null}
          </dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Next agent</dt>
          <dd className="mt-0.5 text-studio-accent">{session?.next_agent?.trim() || "—"}</dd>
        </div>
        <div className="sm:col-span-2">
          <dt className="text-xs uppercase tracking-wide text-slate-500">Branch</dt>
          <dd className="mt-0.5 truncate font-mono text-xs text-slate-300">
            {session?.branch?.trim() || "—"}
          </dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Stage complete</dt>
          <dd className="mt-0.5 text-slate-200">{session?.stage_complete ?? "—"}</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Routing</dt>
          <dd className="mt-0.5">
            <Link to="/observability" className="text-xs text-studio-accent hover:underline">
              View activity timeline
            </Link>
          </dd>
        </div>
      </dl>
    </div>
  );
}
