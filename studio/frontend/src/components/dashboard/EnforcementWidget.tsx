import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { studioApi } from "../../api/client";
import { formatEventTimestamp, payloadSummary, pickLastGatewayDeny } from "../../api/obsQuery";

export function EnforcementWidget() {
  const timeline = useQuery({
    queryKey: ["studio", "dashboard", "gateway-deny"],
    queryFn: () => studioApi.obsTimeline({ category: "gateway", limit: 50 }),
    refetchInterval: 60_000,
  });

  const deny = timeline.data ? pickLastGatewayDeny(timeline.data.events) : null;

  return (
    <div className="rounded-xl border border-slate-800 bg-surface-card p-5">
      <div className="flex items-start justify-between gap-4">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
          Enforcement (fail-closed)
        </h2>
        <Link
          to="/observability?category=gateway"
          className="text-xs text-studio-accent hover:underline"
        >
          Full timeline →
        </Link>
      </div>
      {timeline.isLoading ? (
        <p className="mt-4 text-sm text-slate-400">Loading gateway events…</p>
      ) : timeline.isError ? (
        <p className="mt-4 text-sm text-red-300/90">{timeline.error.message}</p>
      ) : deny ? (
        <dl className="mt-4 space-y-2 text-sm">
          <div className="flex justify-between gap-4">
            <dt className="text-slate-500">Last deny</dt>
            <dd className="font-mono text-xs text-sky-200">{deny.event_type}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-slate-500">When</dt>
            <dd className="text-slate-200">{formatEventTimestamp(deny.timestamp)}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Summary</dt>
            <dd className="mt-1 font-mono text-xs text-amber-100/90">{payloadSummary(deny)}</dd>
          </div>
          {deny.correlation.card ? (
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Card</dt>
              <dd className="text-slate-200">{deny.correlation.card}</dd>
            </div>
          ) : null}
        </dl>
      ) : (
        <p className="mt-4 text-sm text-slate-400">
          No <code className="text-slate-300">gateway.shell_denied</code> events in the recent
          timeline. Hook denials appear here when the write gateway blocks a command.
        </p>
      )}
    </div>
  );
}
