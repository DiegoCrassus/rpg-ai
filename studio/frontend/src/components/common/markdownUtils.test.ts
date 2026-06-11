import { describe, expect, it } from "vitest";

import { splitFrontmatter } from "./markdownUtils";

describe("splitFrontmatter", () => {
  it("splits yaml frontmatter from body", () => {
    const raw = "---\nname: qa\ndescription: test\n---\n\n# Title\n\nBody";
    const { frontmatter, body } = splitFrontmatter(raw);
    expect(frontmatter).toContain("name: qa");
    expect(body).toContain("# Title");
    expect(body).not.toContain("name: qa");
  });

  it("returns full content when no frontmatter", () => {
    const raw = "# Only markdown";
    expect(splitFrontmatter(raw).body).toBe(raw);
    expect(splitFrontmatter(raw).frontmatter).toBeNull();
  });
});
