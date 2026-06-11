import { useCallback, useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { studioApi } from "../api/client";
import { mergeTimelineEvents } from "../api/obsQuery";
import { DerivedBanner } from "../components/common/DerivedBanner";
import { PageHeader } from "../components/common/PageHeader";
import { CategoryContextBanner } from "../components/observability/CategoryContextBanner";
import { CorrelationPanel } from "../components/observability/CorrelationPanel";
import { ObsFiltersBar } from "../components/observability/ObsFiltersBar";
import { TimelineEventRow } from "../components/observability/TimelineEventRow";
import { useStudioObsStream } from "../hooks/useStudioObsStream";
import type { ObsFilterParams, ObsStreamStatus, StudioEvent } from "../types/observability";

const DEFAULT_LIMIT = 100;

const STREAM_LABEL: Record<ObsStreamStatus, string> = {
  idle: "SSE idle",
  connecting: "Connecting…",
  open: "Live",
  error: "SSE error — retry by refreshing",
  closed: "Disconnected",
};

function streamBadgeClass(status: ObsStreamStatus): string {
  if (status === "open") return "border-emerald-500/50 bg-emerald-500/10 text-emerald-200";
  if (status === "error") return "border-studio-fail/50 bg-red-950/40 text-red-200";
  if (status === "connecting") return "border-studio-accent/40 bg-studio-accent/10 text-sky-200";
  return "border-slate-600 bg-slate-800/60 text-slate-400";
}

export function ObservabilityPage() {
  const [filters, setFilters] = useState<ObsFilterParams>({ limit: DEFAULT_LIMIT });
  const [events, setEvents] = useState<StudioEvent[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const filterKey = useMemo(() => JSON.stringify(filters), [filters]);

  const timelineQuery = useQuery({
    queryKey: ["studio", "obs", "timeline", filters],
    queryFn: () => studioApi.obsTimeline(filters),
    refetchInterval: 60_000,
  });

  useEffect(() => {
    if (timelineQuery.data?.events) {
      setEvents(timelineQuery.data.events);
      setSelectedId((current) => {
        if (current && timelineQuery.data!.events.some((e) => e.event_id === current)) {
          return current;
        }
        const list = timelineQuery.data!.events;
        const last = list[list.length - 1];
        return last?.event_id ?? null;
      });
    }
  }, [timelineQuery.data]);

  const onStreamEvent = useCallback((event: StudioEvent) => {
    setEvents((prev) => mergeTimelineEvents(prev, [event]));
    setSelectedId((current) => current ?? event.event_id);
  }, []);

  const [sseSince, setSseSince] = useState<string | null>(null);

  useEffect(() => {
    setSseSince(null);
  }, [filterKey]);

  useEffect(() => {
    const list = timelineQuery.data?.events;
    const last = list?.[list.length - 1];
    if (last) {
      setSseSince((prev) => prev ?? last.timestamp);
    }
  }, [timelineQuery.data]);

  const streamStatus = useStudioObsStream({
    enabled: !timelineQuery.isError && !timelineQuery.isLoading,
    filters,
    since: sseSince,
    onEvent: onStreamEvent,
  });

  const selectedEvent = useMemo(
    () => events.find((e) => e.event_id === selectedId) ?? null,
    [events, selectedId],
  );

  if (timelineQuery.isError) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <DerivedBanner />
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/40 p-4 text-red-200">
          <p className="font-medium">Cannot load observability timeline</p>
          <p className="mt-1 text-sm">
            Start the backend with <code className="text-red-100">make studio-dev</code>, then refresh.
          </p>
          <p className="mt-2 text-xs text-red-300/80">{timelineQuery.error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-7rem)] max-w-6xl flex-col gap-4 overflow-hidden">
      <div className="shrink-0 space-y-4">
        <DerivedBanner />
        <PageHeader
          pageId="observability"
          subtitle="Unified timeline from gateway, handoff, gate, and obs runs · SSE /studio/obs/events"
          aside={
            <span
              className={`rounded-full border px-3 py-1 text-xs font-medium ${streamBadgeClass(streamStatus)}`}
            >
              {STREAM_LABEL[streamStatus]}
            </span>
          }
        />

        <ObsFiltersBar
          filters={filters}
          onChange={(next) => setFilters({ limit: DEFAULT_LIMIT, ...next })}
          onReset={() => setFilters({ limit: DEFAULT_LIMIT })}
        />
        {filters.category ? <CategoryContextBanner category={filters.category} /> : null}
      </div>

      <div className="grid min-h-0 flex-1 gap-4 lg:grid-cols-[minmax(0,12fr)_minmax(420px,13fr)]">
        <section className="flex min-h-0 flex-col overflow-hidden" key={filterKey}>
          <div className="mb-2 shrink-0 text-xs text-slate-500">
            {timelineQuery.isLoading ? "Loading…" : `${events.length} event(s)`}
            {timelineQuery.data?.count != null && !timelineQuery.isLoading
              ? ` · API count ${timelineQuery.data.count}`
              : null}
          </div>
          {timelineQuery.isLoading && events.length === 0 ? (
            <p className="text-slate-400">Loading timeline…</p>
          ) : events.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center text-sm text-slate-500">
              No events match the current filters. Trigger gateway or handoff activity, then refresh.
            </div>
          ) : (
            <ul className="min-h-0 flex-1 space-y-1 overflow-y-auto pr-1">
              {[...events].reverse().map((event) => (
                <li key={event.event_id}>
                  <TimelineEventRow
                    event={event}
                    selected={event.event_id === selectedId}
                    onSelect={() => setSelectedId(event.event_id)}
                  />
                </li>
              ))}
            </ul>
          )}
        </section>

        <aside className="flex min-h-0 flex-col overflow-hidden">
          {selectedEvent ? (
            <CorrelationPanel event={selectedEvent} />
          ) : (
            <div
              className="flex flex-1 items-center justify-center rounded-xl border border-dashed border-slate-700 p-6 text-center text-sm text-slate-500"
              data-testid="obs-detail-panel"
            >
              Select an event to inspect correlation and payload.
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
