import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { formatEventTimestamp, payloadSummary } from "../../api/obsQuery";
import { studioApi } from "../../api/client";
import { describeCategory } from "../observability/obsHelp";

const CATEGORY_STYLES = {
  gateway: "text-sky-300",
  obs: "text-emerald-300",
  handoff: "text-violet-300",
  gate: "text-amber-300",
} as const;

type SdlcActivityFeedProps = {
  activeCard?: string | null;
};

export function SdlcActivityFeed({ activeCard }: SdlcActivityFeedProps) {
  const [scope, setScope] = useState<"all" | "card">("all");
  const card = activeCard?.trim().toUpperCase() ?? "";
  const useCardFilter = scope === "card" && Boolean(card);

  const timelineQuery = useQuery({
    queryKey: ["studio", "dashboard", "activity", scope, card],
    queryFn: () =>
      studioApi.obsTimeline({
        limit: 30,
        ...(useCardFilter ? { card } : {}),
      }),
    refetchInterval: 45_000,
    staleTime: 30_000,
  });

  const events = useMemo(() => {
    const list = timelineQuery.data?.events ?? [];
    return [...list].reverse().slice(0, 20);
  }, [timelineQuery.data?.events]);

  return (
    <div className="rounded-xl border border-slate-800 bg-surface-card p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
            SDLC activity
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            Gateway, handoff, gate, and observability events
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="inline-flex rounded-md border border-slate-700 p-0.5 text-xs">
            <button
              type="button"
              onClick={() => setScope("all")}
              className={[
                "rounded px-2.5 py-1",
                scope === "all" ? "bg-studio-accent/20 text-studio-accent" : "text-slate-400",
              ].join(" ")}
            >
              All
            </button>
            <button
              type="button"
              disabled={!card}
              onClick={() => setScope("card")}
              className={[
                "rounded px-2.5 py-1 disabled:opacity-40",
                scope === "card" ? "bg-studio-accent/20 text-studio-accent" : "text-slate-400",
              ].join(" ")}
            >
              {card || "Card"}
            </button>
          </div>
          <Link to="/observability" className="text-xs text-studio-accent hover:underline">
            View all
          </Link>
        </div>
      </div>

      {timelineQuery.isLoading ? (
        <p className="mt-4 text-sm text-slate-400">Loading activity…</p>
      ) : timelineQuery.isError ? (
        <p className="mt-4 text-sm text-amber-300/90">
          Cannot load timeline — start the API and ensure observability data exists.
        </p>
      ) : events.length === 0 ? (
        <p className="mt-4 text-sm text-slate-500">
          No events yet. Run agents or gateway activity to populate the timeline.
        </p>
      ) : (
        <ul className="mt-3 max-h-64 space-y-1 overflow-y-auto pr-1">
          {events.map((event) => {
            const categoryHelp = describeCategory(event.category);
            const style = CATEGORY_STYLES[event.category];
            return (
              <li
                key={event.event_id}
                className="rounded-md border border-slate-800/80 bg-slate-900/40 px-3 py-2 text-sm"
              >
                <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
                  <span className="font-mono text-[11px] text-slate-500">
                    {formatEventTimestamp(event.timestamp)}
                  </span>
                  <span className={`text-[10px] uppercase tracking-wide ${style}`}>
                    {event.category}
                  </span>
                  <span className="font-mono text-[11px] text-slate-300">{event.event_type}</span>
                  {event.correlation?.card ? (
                    <span className="font-mono text-[10px] text-slate-500">
                      {event.correlation.card}
                    </span>
                  ) : null}
                </div>
                <p className="mt-0.5 truncate text-xs text-slate-400" title={categoryHelp.description}>
                  {payloadSummary(event)}
                </p>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
