import { describe, expect, it } from "vitest";

import {
  buildConfigProposalRequest,
  isValidSlug,
  normalizeSlug,
  targetPathForSlug,
  templateContent,
} from "./configDraft";

describe("normalizeSlug", () => {
  it("lowercases and hyphenates", () => {
    expect(normalizeSlug("My Agent")).toBe("my-agent");
  });
});

describe("targetPathForSlug", () => {
  it("maps agent slug to agents path", () => {
    expect(targetPathForSlug("agent", "my-agent")).toBe(".cursor/agents/my-agent.md");
  });

  it("maps skill slug to SKILL.md path", () => {
    expect(targetPathForSlug("skill", "plane-sdlc")).toBe(".cursor/skills/plane-sdlc/SKILL.md");
  });
});

describe("buildConfigProposalRequest", () => {
  it("uses create_file for new paths", () => {
    const request = buildConfigProposalRequest({
      kind: "command",
      path: ".cursor/commands/demo.md",
      content: "# Demo\n",
      title: "Add demo command",
      card: "RPG-87",
      mode: "create",
      exists: false,
    });
    expect(request.ops[0]?.op).toBe("create_file");
    expect(request.simulated_gate).toEqual({ stage: "sdlc_meta", card: "RPG-87" });
  });

  it("uses replace_block when editing existing file", () => {
    const request = buildConfigProposalRequest({
      kind: "agent",
      path: ".cursor/agents/qa.md",
      content: "# QA\n",
      title: "Update QA agent",
      card: "RPG-87",
      mode: "edit",
      exists: true,
    });
    expect(request.ops[0]?.op).toBe("replace_block");
  });
});

describe("templateContent", () => {
  it("includes agent frontmatter", () => {
    expect(templateContent("agent", "helper", "Does things")).toContain("name: helper");
  });

  it("validates slug pattern", () => {
    expect(isValidSlug("my-agent")).toBe(true);
    expect(isValidSlug("My-Agent")).toBe(false);
  });
});
