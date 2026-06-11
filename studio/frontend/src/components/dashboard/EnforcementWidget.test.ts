import { describe, expect, it } from "vitest";

import { pickLastGatewayDeny } from "../../api/obsQuery";
import type { StudioEvent } from "../../types/observability";

function denyEvent(command: string): StudioEvent {
  return {
    schema_version: "1",
    event_id: "e1",
    event_type: "gateway.shell_denied",
    category: "gateway",
    timestamp: "2026-06-04T12:00:00Z",
    source: "sdlc_pre_gateway",
    correlation_id: "card:INVES-92",
    correlation: { card: "INVES-92" },
    payload: { command },
  };
}

describe("pickLastGatewayDeny", () => {
  it("returns the most recent gateway.shell_denied", () => {
    const events = [
      {
        ...denyEvent("git push"),
        event_id: "old",
        timestamp: "2026-06-04T10:00:00Z",
      },
      denyEvent("rm -rf /"),
    ];
    const last = pickLastGatewayDeny(events);
    expect(last?.payload.command).toBe("rm -rf /");
  });

  it("returns null when no deny events", () => {
    expect(
      pickLastGatewayDeny([
        {
          ...denyEvent("x"),
          event_type: "handoff.updated",
          category: "handoff",
        },
      ]),
    ).toBeNull();
  });
});
