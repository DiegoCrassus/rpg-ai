import type { EvidenceFields } from "../../types/evidence";

function bulletList(items: string[]): string {
  if (items.length === 0) {
    return "- _(none)_";
  }
  return items.map((item) => `- ${item}`).join("\n");
}

function recordLines(record: Record<string, string | string[]>): string {
  return Object.entries(record)
    .map(([key, value]) => {
      if (Array.isArray(value)) {
        return `- **${key}:** ${value.join(", ") || "_(none)_"}`;
      }
      return `- **${key}:** ${value}`;
    })
    .join("\n");
}

/** Markdown suitable for pasting into a Plane work item comment. */
export function formatEvidenceMarkdown(fields: EvidenceFields): string {
  const sections = [
    `## ${fields.title}`,
    `**Card:** ${fields.card}`,
    "",
    "### Summary",
    fields.summary,
    "",
    "### Problems solved",
    bulletList(fields.problems_solved),
    "",
    "### Technical",
    [
      `- **modules:** ${fields.technical.modules.join(", ") || "_(none)_"}`,
      `- **decisions:** ${fields.technical.decisions.join("; ") || "_(none)_"}`,
      `- **files_changed:** ${fields.technical.files_changed.join(", ") || "_(none)_"}`,
    ].join("\n"),
    "",
    "### Validation",
    recordLines(fields.validation),
    "",
    "### Artifacts",
    recordLines(fields.artifacts),
    "",
    "### Context for future",
    bulletList(fields.context_for_future),
    "",
    "---",
    "_Derived Studio projection — verify with real QA, doctor, and CI before posting as authoritative evidence._",
  ];
  return sections.join("\n");
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function htmlList(items: string[]): string {
  if (items.length === 0) {
    return "<p><em>(none)</em></p>";
  }
  return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

/** HTML fragment for rich-text paste targets. */
export function formatEvidenceHtml(fields: EvidenceFields): string {
  return [
    `<h2>${escapeHtml(fields.title)}</h2>`,
    `<p><strong>Card:</strong> ${escapeHtml(fields.card)}</p>`,
    "<h3>Summary</h3>",
    `<p>${escapeHtml(fields.summary)}</p>`,
    "<h3>Problems solved</h3>",
    htmlList(fields.problems_solved),
    "<h3>Technical</h3>",
    htmlList([
      `modules: ${fields.technical.modules.join(", ") || "(none)"}`,
      `decisions: ${fields.technical.decisions.join("; ") || "(none)"}`,
      `files: ${fields.technical.files_changed.join(", ") || "(none)"}`,
    ]),
    "<h3>Validation</h3>",
    htmlList(Object.entries(fields.validation).map(([k, v]) => `${k}: ${v}`)),
    "<h3>Artifacts</h3>",
    htmlList(
      Object.entries(fields.artifacts).map(([k, v]) =>
        Array.isArray(v) ? `${k}: ${v.join(", ")}` : `${k}: ${v}`,
      ),
    ),
    "<h3>Context for future</h3>",
    htmlList(fields.context_for_future),
    "<hr>",
    "<p><em>Derived Studio projection — verify with real QA, doctor, and CI.</em></p>",
  ].join("");
}
