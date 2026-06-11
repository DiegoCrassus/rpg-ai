import { describe, expect, it } from "vitest";

import { PAGE_HELP, pageHelpFor } from "./pageHelp";

describe("pageHelp", () => {
  it("defines help for every primary nav screen", () => {
    const ids = [
      "dashboard",
      "workflows",
      "agents",
      "rules",
      "commands",
      "registry",
      "validation",
      "simulation",
      "assistance",
      "observability",
      "evidence",
      "settings",
    ] as const;
    for (const id of ids) {
      const help = pageHelpFor(id);
      expect(PAGE_HELP[id].title).toBe(help.title);
      expect(help.summary.length).toBeGreaterThan(20);
    }
  });
});
