import { useMemo } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { studioApi } from "../../api/client";
import type { DashboardSummary } from "../../types/studio";
import { planeStateGroupClass } from "./planeStateStyle";

import { PLANE_CARD_PATTERN } from "../../constants/plane";

type ActiveWorkPanelProps = {
  session?: DashboardSummary["session"];
  handoffPresent?: boolean;
};

export function ActiveWorkPanel({ session, handoffPresent }: ActiveWorkPanelProps) {
  const card = session?.card?.trim().toUpperCase() ?? "";
  const cardValid = PLANE_CARD_PATTERN.test(card);

  const planeQuery = useQuery({
    queryKey: ["studio", "integrations", "plane", card],
    queryFn: () => studioApi.planeCard(card),
    enabled: cardValid,
    retry: false,
    staleTime: 60_000,
  });

  const epicCard = useMemo(() => {
    if (!cardValid) return null;
    if (planeQuery.data?.parent) return planeQuery.data.parent;
    return card;
  }, [card, cardValid, planeQuery.data?.parent]);

  const epicQuery = useQuery({
    queryKey: ["studio", "integrations", "plane", "epic-children", epicCard],
    queryFn: () => studioApi.planeEpicChildren(epicCard!),
    enabled: Boolean(epicCard),
    retry: false,
    staleTime: 60_000,
  });

  const plane = planeQuery.data;
  const epic = epicQuery.data;
  const showEpic = (epic?.total ?? 0) > 0;

  return (
    <div className="rounded-xl border border-slate-800 bg-surface-card p-5">
      <div className="flex items-start justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
          Active work
        </h2>
        <div className="flex flex-wrap items-center gap-3">
          {session?.execution_active || session?.gate_open ? (
            <Link
              to="/workflows"
              data-testid="dashboard-track-workflow"
              className="rounded-md border border-sky-500/50 bg-sky-500/10 px-3 py-1.5 text-xs font-medium text-sky-200 hover:bg-sky-500/20"
            >
              Track in Workflow
            </Link>
          ) : null}
          {plane ? (
            <a
              href={plane.plane_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-studio-accent hover:underline"
            >
              Open in Plane
            </a>
          ) : null}
        </div>
      </div>

      {plane ? (
        <div className="mt-3 rounded-lg border border-slate-700/80 bg-slate-900/50 p-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-sm font-medium text-white">{plane.card}</span>
            <span
              className={`rounded border px-1.5 py-0.5 text-[10px] uppercase tracking-wide ${planeStateGroupClass(plane.state.group)}`}
            >
              {plane.state.name}
            </span>
            {plane.priority ? (
              <span className="text-[10px] uppercase text-slate-500">{plane.priority}</span>
            ) : null}
          </div>
          <p className="mt-1.5 text-sm leading-snug text-slate-200">{plane.name}</p>
          {plane.parent ? (
            <p className="mt-1 text-xs text-slate-500">
              Epic: <span className="font-mono text-slate-400">{plane.parent}</span>
            </p>
          ) : null}
        </div>
      ) : null}

      <dl className="mt-4 space-y-2 text-sm">
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Gate</dt>
          <dd className={session?.gate_open ? "text-emerald-400" : "text-slate-300"}>
            {session?.gate_open ? "Open" : "Closed"}
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Card</dt>
          <dd className="font-medium text-white">{session?.card ?? "—"}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Branch</dt>
          <dd className="truncate font-mono text-xs text-slate-200">{session?.branch ?? "—"}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Stage</dt>
          <dd className="text-slate-200">{session?.stage ?? "—"}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Next agent</dt>
          <dd className="text-studio-accent">{session?.next_agent ?? "—"}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Stage complete</dt>
          <dd className="text-slate-200">{session?.stage_complete ?? "—"}</dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-slate-500">Handoff file</dt>
          <dd className="text-slate-200">{handoffPresent ? "Present" : "Missing"}</dd>
        </div>
      </dl>

      {cardValid && planeQuery.isError ? (
        <p className="mt-3 text-xs text-amber-300/90">
          Plane card unavailable — set PLANE_API_KEY or check card id.
        </p>
      ) : null}

      {showEpic ? (
        <div className="mt-4 border-t border-slate-800 pt-3">
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Epic scope · {epic?.epic} ({epic?.total} children)
          </p>
          <ul className="mt-2 max-h-32 space-y-1 overflow-y-auto text-xs">
            {Object.entries(epic?.children_by_state ?? {}).flatMap(([stateName, children]) =>
              children.map((child) => (
                <li
                  key={child.card}
                  className="flex items-center justify-between gap-2 rounded px-1 py-0.5 hover:bg-slate-800/60"
                >
                  <span className="truncate text-slate-300">
                    <span className="font-mono text-slate-400">{child.card}</span> {child.name}
                  </span>
                  <span className="shrink-0 text-slate-500">{stateName}</span>
                </li>
              )),
            )}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
