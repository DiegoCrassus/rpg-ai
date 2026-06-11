import { describe, expect, it } from "vitest";

import { CATEGORY_HELP, describeEventType, describeCategory } from "./obsHelp";

describe("obsHelp", () => {
  it("describes known event types", () => {
    expect(describeEventType("gateway.shell_denied")).toContain("shell command");
    expect(describeEventType("handoff.updated")).toContain("Handoff");
  });

  it("falls back for unknown event types", () => {
    expect(describeEventType("custom.unknown")).toContain("custom.unknown");
  });

  it("returns category help for all categories", () => {
    for (const key of Object.keys(CATEGORY_HELP)) {
      const help = describeCategory(key as keyof typeof CATEGORY_HELP);
      expect(help.title.length).toBeGreaterThan(0);
      expect(help.description.length).toBeGreaterThan(10);
    }
  });
});
