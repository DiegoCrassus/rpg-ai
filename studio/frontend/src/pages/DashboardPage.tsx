import { useQuery } from "@tanstack/react-query";

import { studioApi } from "../api/client";
import { DerivedBanner } from "../components/common/DerivedBanner";
import { PageHeader } from "../components/common/PageHeader";
import { ActiveWorkPanel } from "../components/dashboard/ActiveWorkPanel";
import { EnforcementWidget } from "../components/dashboard/EnforcementWidget";
import { PlaneWorkFeed } from "../components/dashboard/PlaneWorkFeed";
import { SdlcActivityFeed } from "../components/dashboard/SdlcActivityFeed";

function StatusCard({
  title,
  value,
  hint,
}: {
  title: string;
  value: string;
  hint?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-surface-card p-4">
      <p className="text-xs uppercase tracking-wide text-slate-500">{title}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
      {hint ? <p className="mt-1 text-xs text-slate-400">{hint}</p> : null}
    </div>
  );
}

export function DashboardPage() {
  const summary = useQuery({
    queryKey: ["studio", "dashboard", "summary"],
    queryFn: studioApi.dashboardSummary,
    refetchInterval: 30_000,
  });
  const health = useQuery({
    queryKey: ["studio", "health"],
    queryFn: studioApi.health,
  });
  const readiness = useQuery({
    queryKey: ["studio", "readiness"],
    queryFn: studioApi.readiness,
  });

  const dash = summary.data;
  const authority =
    dash?.authority ?? readiness.data?.readiness?.authority ?? "derived_non_authoritative";

  if (summary.isError || health.isError) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <DerivedBanner authority={authority} />
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/40 p-4 text-red-200">
          <p className="font-medium">Cannot reach Studio API</p>
          <p className="mt-1 text-sm">
            Start the backend with <code className="text-red-100">make studio-dev</code> or{" "}
            <code className="text-red-100">uvicorn</code> on port 8100, then refresh.
          </p>
          <p className="mt-2 text-xs text-red-300/80">
            {summary.error?.message ?? health.error?.message}
          </p>
        </div>
      </div>
    );
  }

  const session = dash?.session;
  const ready = dash?.readiness;
  const canvas = dash?.canvas;

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <DerivedBanner authority={authority} />
      <PageHeader
        pageId="dashboard"
        subtitle={`Read-only SDLC health from Studio Service · API ${
          health.data?.version ? `v${health.data.version}` : ""
        }`}
      />

      {summary.isLoading ? (
        <p className="text-slate-400">Loading dashboard…</p>
      ) : (
        <>
          <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatusCard
              title="MVP readiness"
              value={ready?.mvp_ready ? "Ready" : "Not ready"}
              hint={ready?.overall_status ?? "—"}
            />
            <StatusCard
              title="Checks"
              value={`${ready?.pass ?? 0} pass · ${ready?.warn ?? 0} warn · ${ready?.fail ?? 0} fail`}
            />
            <StatusCard
              title="Session gate"
              value={session?.gate_open ? "Open" : "Closed"}
              hint={[session?.card, session?.stage].filter(Boolean).join(" · ") || undefined}
            />
            <StatusCard
              title="Canvas"
              value={
                canvas?.available
                  ? `${canvas.nodes ?? 0} nodes · ${canvas.edges ?? 0} edges`
                  : "Unavailable"
              }
            />
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            <ActiveWorkPanel session={session} handoffPresent={dash?.handoff_present} />
            <PlaneWorkFeed />
          </section>

          <SdlcActivityFeed activeCard={session?.card} />

          <section className="grid gap-4 lg:grid-cols-2">
            <EnforcementWidget />
            <div className="rounded-xl border border-slate-800 bg-surface-card p-5">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
                Service health
              </h2>
              <dl className="mt-4 space-y-2 text-sm">
                <div className="flex justify-between gap-4">
                  <dt className="text-slate-500">Status</dt>
                  <dd className="text-emerald-400">{health.data?.status ?? "—"}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-slate-500">Repo reachable</dt>
                  <dd className="text-slate-200">
                    {health.data?.repo_root_reachable ? "Yes" : "No"}
                  </dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-slate-500">Readiness authority</dt>
                  <dd className="font-mono text-xs text-amber-200/90">{authority}</dd>
                </div>
                {readiness.data?.readiness?.execution_mode ? (
                  <div className="flex justify-between gap-4">
                    <dt className="text-slate-500">Execution mode</dt>
                    <dd className="font-mono text-xs text-slate-300">
                      {readiness.data.readiness.execution_mode}
                    </dd>
                  </div>
                ) : null}
              </dl>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
