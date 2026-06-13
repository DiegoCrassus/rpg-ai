import { describe, expect, it } from "vitest";

import { formatEvidenceHtml, formatEvidenceMarkdown } from "./formatEvidenceComment";
import type { EvidenceFields } from "../../types/evidence";

const sampleFields: EvidenceFields = {
  card: "RPG-91",
  title: "[AI][FRONTEND] Evidence UI",
  summary: "Delivery screen wired to draft API.",
  problems_solved: ["Reduced tool switching for operators"],
  technical: {
    modules: ["studio/frontend/src/pages"],
    decisions: ["Read-only integrations"],
    files_changed: ["EvidencePage.tsx"],
  },
  validation: {
    tests: "npm run build",
    doctor: "not run",
    ci: "not run",
  },
  artifacts: {
    pr: "n/a",
    branch: "feature/RPG-91-studio-ui-evidence-delivery-s7",
    commit: "n/a",
    docs: [".sdlc/templates/plane/evidence-template.json"],
  },
  context_for_future: ["Run QA with live Plane/GitHub tokens"],
};

describe("formatEvidenceMarkdown", () => {
  it("includes card, sections, and disclaimer", () => {
    const md = formatEvidenceMarkdown(sampleFields);
    expect(md).toContain("## [AI][FRONTEND] Evidence UI");
    expect(md).toContain("**Card:** RPG-91");
    expect(md).toContain("### Validation");
    expect(md).toContain("- **tests:** npm run build");
    expect(md).toContain("Derived Studio projection");
  });
});

describe("formatEvidenceHtml", () => {
  it("escapes HTML in field values", () => {
    const html = formatEvidenceHtml({
      ...sampleFields,
      summary: "Check <script> & quotes",
    });
    expect(html).toContain("Check &lt;script&gt; &amp; quotes");
    expect(html).not.toContain("<script>");
  });
});
