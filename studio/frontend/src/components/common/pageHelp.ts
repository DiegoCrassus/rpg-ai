export type PageHelpId =
  | "dashboard"
  | "builder"
  | "workflows"
  | "agents"
  | "rules"
  | "commands"
  | "registry"
  | "validation"
  | "simulation"
  | "assistance"
  | "observability"
  | "evidence"
  | "settings";

export type PageHelp = {
  title: string;
  subtitle?: string;
  summary: string;
  bullets?: string[];
};

export const PAGE_HELP: Record<PageHelpId, PageHelp> = {
  dashboard: {
    title: "Dashboard",
    subtitle: "Read-only SDLC health from Studio Service",
    summary:
      "Overview of repo readiness, session gate, Plane workboard, SDLC activity timeline, and gateway enforcement.",
    bullets: [
      "MVP readiness comes from make sdlc-doctor / readiness API",
      "Active work enriches session gate with live Plane card and epic children",
      "When the gate is open, Active work shows Track in Workflow to follow the live stage",
      "Plane workboard lists recent cards; SDLC activity shows gateway/handoff/gate/obs events",
      "All data is derived — apply changes via git/Plane, not Studio writes",
    ],
  },
  builder: {
    title: "Workflow Builder",
    subtitle: "Author lifecycle transitions and agent assignments",
    summary:
      "Drag stages and agents onto the canvas, wire transitions, and export propose-only patches for git review.",
    bullets: [
      "Does not apply changes to the repo directly",
      "Aligns with transitions.yaml and pipeline agents",
      "Export produces a reviewable patch for Plane/git workflow",
    ],
  },
  workflows: {
    title: "Workflow",
    subtitle: "Live SDLC lifecycle diagram with session tracking",
    summary:
      "Step-by-step view of the Delivery and Incident tracks. Live session shows which track is operating and which stage is active.",
    bullets: [
      "Delivery pipeline: Ticket → Observability — standard feature and bugfix path",
      "Incident track: Incident → Auto Fix — parallel corrective path sharing the implementation gate",
      "Select a track to explore; the Active badge marks the track running in session-gate",
      "Click any step for agent ownership, transitions, and how the two tracks relate",
    ],
  },
  agents: {
    title: "Agents & Subagents",
    subtitle: "Browse and draft .cursor/agents definitions",
    summary:
      "List agent files under allowlisted paths, edit or draft from template, export propose-only patches.",
    bullets: [
      "Matches Cursor subagents referenced in transitions.yaml",
      "New drafts require a valid slug; export does not write disk directly",
      "Simulated card field tags proposals for Plane traceability",
    ],
  },
  rules: {
    title: "Rules & Skills",
    subtitle: "Browse and draft .cursor/rules and skills",
    summary:
      "Switch between Rules and Skills tabs to edit allowlisted Cursor artifacts and export patches.",
    bullets: [
      "Rules shape orchestrator/subagent behavior in Cursor",
      "Skills are referenced by agents and transition inspectors",
      "Same propose-only export flow as Agents and Commands",
    ],
  },
  commands: {
    title: "Commands",
    subtitle: "Browse and draft .cursor/commands slash commands",
    summary:
      "Edit existing slash commands or draft new ones from template; export unified diffs for review.",
    bullets: [
      "Commands appear in Cursor command palette after merge",
      "Paths are constrained to registry allowlist",
      "Validate proposal before sharing PR evidence",
    ],
  },
  registry: {
    title: "Registry Explorer",
    subtitle: "Manifest graph of SDLC registry relationships",
    summary:
      "Visualize nodes and edges from .sdlc/registry with broken-ref counts and selection summary.",
    bullets: [
      "Read-only graph — fixes happen in repo YAML, not Studio",
      "Use filters to reduce noise on large manifests",
      "Broken refs highlight drift between registry files",
    ],
  },
  validation: {
    title: "Validation Center",
    subtitle: "Run doctor, gateway, and contract checks on demand",
    summary:
      "Trigger validation endpoints and inspect pass/warn/fail summaries for the active repo snapshot.",
    bullets: [
      "Doctor maps to make sdlc-doctor checks",
      "Results are point-in-time — re-run after changes",
      "Use before marking Plane cards Done or opening PRs",
    ],
  },
  simulation: {
    title: "Simulation",
    subtitle: "Preview workflow paths without mutating the repo",
    summary:
      "Simulate SDLC stage progression and gate outcomes to understand routing before implementation.",
    bullets: [
      "Simulation does not open gates or write files",
      "Useful for onboarding and debugging orchestrator handoffs",
      "Correlates with session-gate.json when a card is active",
    ],
  },
  assistance: {
    title: "Assistance",
    subtitle: "AI-assisted workflow hints (propose-only)",
    summary:
      "Request structured assistance suggestions tied to the current workflow context — export as proposals.",
    bullets: [
      "Studio does not embed Cursor chat — continue in IDE",
      "Suggestions reference allowlisted agents/skills",
      "Treat output as draft until reviewed and merged",
    ],
  },
  observability: {
    title: "Observability",
    subtitle: "Unified timeline from gateway, handoff, gate, and obs runs",
    summary:
      "Filter and inspect SDLC events in real time via REST timeline and SSE /studio/obs/events.",
    bullets: [
      "Categories: gateway, handoff, gate, obs — use ⓘ icons for detail",
      "Select a row to inspect correlation fields and JSON payload",
      "Timeline and detail panel scroll independently",
    ],
  },
  evidence: {
    title: "Evidence & Delivery",
    subtitle: "Plane/GitHub evidence helpers for finish-change",
    summary:
      "Compose QA evidence comments, inspect PR checks, and follow finish-change workflow for delivery.",
    bullets: [
      "Evidence posts to Plane — not stored in repo specs/",
      "GitHub pulls and checks are read-only integrations",
      "Use after QA pass and Reviewer APPROVE before merge",
    ],
  },
  settings: {
    title: "Settings",
    subtitle: "Studio meta configuration (roadmap)",
    summary:
      "Future home for Studio Service URL, theme, and operator preferences. Currently a placeholder.",
    bullets: [
      "No secrets stored in browser localStorage except sidebar collapse",
      "Repo root is detected from Studio API health endpoint",
    ],
  },
};

export function pageHelpFor(id: PageHelpId): PageHelp {
  return PAGE_HELP[id];
}
