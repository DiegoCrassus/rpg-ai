import { afterEach, describe, expect, it, vi } from "vitest";

import {
  matchesObsFilters,
  mergeTimelineEvents,
  obsQueryString,
  studioObsEventsUrl,
} from "./obsQuery";
import type { StudioEvent } from "../types/observability";

const baseEvent: StudioEvent = {
  schema_version: "1.0",
  event_id: "evt_a",
  event_type: "handoff.updated",
  category: "handoff",
  timestamp: "2026-06-03T10:00:00Z",
  source: "handoff_watcher",
  correlation_id: "card:INVES-82|run:abc",
  correlation: { card: "INVES-82", run_id: "abc" },
  payload: { next_agent: "qa" },
};

describe("obsQueryString", () => {
  it("builds category and card query params", () => {
    expect(
      obsQueryString({ category: "gateway", card: "INVES-82", limit: 50 }),
    ).toBe("?category=gateway&card=INVES-82&limit=50");
  });

  it("returns empty string when no filters", () => {
    expect(obsQueryString({})).toBe("");
  });
});

describe("studioObsEventsUrl", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("includes since and limit on SSE path", () => {
    vi.stubEnv("VITE_STUDIO_API_URL", "");
    expect(studioObsEventsUrl({ since: "2026-06-03T09:00:00Z", limit: 25 })).toBe(
      "/studio/obs/events?since=2026-06-03T09%3A00%3A00Z&limit=25",
    );
  });
});

describe("matchesObsFilters", () => {
  it("matches card via correlation block", () => {
    expect(matchesObsFilters(baseEvent, { card: "INVES-82" })).toBe(true);
    expect(matchesObsFilters(baseEvent, { card: "INVES-99" })).toBe(false);
  });

  it("matches category and event_type substring", () => {
    expect(matchesObsFilters(baseEvent, { category: "handoff" })).toBe(true);
    expect(matchesObsFilters(baseEvent, { event_type: "handoff." })).toBe(true);
    expect(matchesObsFilters(baseEvent, { category: "gateway" })).toBe(false);
  });
});

describe("mergeTimelineEvents", () => {
  it("dedupes by event_id and sorts by timestamp", () => {
    const later: StudioEvent = {
      ...baseEvent,
      event_id: "evt_b",
      timestamp: "2026-06-03T10:00:01Z",
      event_type: "gateway.shell_denied",
      category: "gateway",
    };
    const merged = mergeTimelineEvents(
      [later, baseEvent],
      [{ ...baseEvent, payload: { next_agent: "implementer" } }],
    );
    expect(merged).toHaveLength(2);
    expect(merged[0].event_id).toBe("evt_a");
    expect(merged[1].event_id).toBe("evt_b");
    expect(merged[0].payload.next_agent).toBe("implementer");
  });
});
