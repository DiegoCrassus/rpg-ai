import { studioApiBase } from "./client";
import type { ObsFilterParams, StudioEvent } from "../types/observability";

export function obsQueryString(filters: ObsFilterParams = {}): string {
  const params = new URLSearchParams();
  if (filters.category) params.set("category", filters.category);
  if (filters.card?.trim()) params.set("card", filters.card.trim());
  if (filters.run_id?.trim()) params.set("run_id", filters.run_id.trim());
  if (filters.event_type?.trim()) params.set("event_type", filters.event_type.trim());
  if (filters.limit != null) params.set("limit", String(filters.limit));
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export function studioObsEventsUrl(options: { since?: string; limit?: number } = {}): string {
  const params = new URLSearchParams();
  if (options.since) params.set("since", options.since);
  params.set("limit", String(options.limit ?? 100));
  const qs = params.toString();
  return `${studioApiBase()}/obs/events?${qs}`;
}

export function matchesObsFilters(event: StudioEvent, filters: ObsFilterParams): boolean {
  if (filters.category && event.category !== filters.category) {
    return false;
  }
  if (filters.card?.trim()) {
    const card = filters.card.trim().toUpperCase();
    const eventCard = event.correlation?.card?.toUpperCase();
    const inCorrelationId = event.correlation_id.toUpperCase().includes(card);
    if (eventCard !== card && !inCorrelationId) {
      return false;
    }
  }
  if (filters.run_id?.trim()) {
    const runId = filters.run_id.trim();
    const eventRun = event.correlation?.run_id;
    const inCorrelationId = event.correlation_id.includes(runId);
    if (eventRun !== runId && !inCorrelationId) {
      return false;
    }
  }
  if (filters.event_type?.trim()) {
    const needle = filters.event_type.trim();
    if (!event.event_type.includes(needle)) {
      return false;
    }
  }
  return true;
}

export function mergeTimelineEvents(
  existing: StudioEvent[],
  incoming: StudioEvent[],
): StudioEvent[] {
  const byId = new Map<string, StudioEvent>();
  for (const event of [...existing, ...incoming]) {
    byId.set(event.event_id, event);
  }
  return [...byId.values()].sort((a, b) => a.timestamp.localeCompare(b.timestamp));
}

export function formatEventTimestamp(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return iso;
  }
  return date.toLocaleString(undefined, {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function pickLastGatewayDeny(events: StudioEvent[]): StudioEvent | null {
  for (let i = events.length - 1; i >= 0; i -= 1) {
    if (events[i].event_type === "gateway.shell_denied") {
      return events[i];
    }
  }
  return null;
}

export function payloadSummary(event: StudioEvent): string {
  const p = event.payload;
  if (event.event_type === "gateway.shell_denied" && typeof p.command === "string") {
    return `denied: ${p.command}`;
  }
  if (event.event_type === "handoff.updated" && typeof p.next_agent === "string") {
    return `next → ${p.next_agent}`;
  }
  if (typeof p.next_agent === "string") {
    return `agent: ${p.next_agent}`;
  }
  const keys = Object.keys(p);
  if (keys.length === 0) {
    return "—";
  }
  return keys.slice(0, 3).join(", ");
}
