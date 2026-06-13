import type { EventCategory } from "../../types/observability";

export type CategoryHelp = {
  title: string;
  description: string;
  examples: string;
};

export const CATEGORY_HELP: Record<EventCategory, CategoryHelp> = {
  gateway: {
    title: "Gateway",
    description:
      "Cursor hook enforcement — blocks unsafe shell commands and routes subagents to match orchestrator-handoff.",
    examples: "gateway.shell_denied, gateway.subagent_start",
  },
  obs: {
    title: "Runs (obs)",
    description:
      "Pipeline observer metrics — task start/end, duration, tokens, and tool calls from SDLC subagent runs.",
    examples: "obs.task_started, obs.task_completed",
  },
  handoff: {
    title: "Handoff",
    description:
      "Orchestrator routing updates when .sdlc/memory/orchestrator-handoff.md changes (next agent, stage, card).",
    examples: "handoff.updated",
  },
  gate: {
    title: "Gate",
    description:
      "Session gate activity — mechanical write blocks and session-gate.json open/close transitions.",
    examples: "session.gate_changed, gate.write_denied",
  },
};

const EVENT_TYPE_HELP: Record<string, string> = {
  "gateway.shell_denied":
    "A shell command was blocked by the pre-gateway (deny pattern or workflow bypass). Check payload.command.",
  "gateway.subagent_start":
    "A Task subagent was requested; logged when routing matches or conflicts with handoff.",
  "gateway.handoff_blocked":
    "Handoff validation failed — incomplete routing, blockers, or evidence mismatch blocked the next step.",
  "handoff.updated":
    "Handoff file changed — see payload for next_agent, stage_complete, and previous_agent.",
  "session.gate_changed":
    "session-gate.json changed — gate opened/closed or card/branch/stage updated.",
  "gate.write_denied":
    "A Write was denied because the SDLC session gate is closed for the active card.",
};

export const FILTER_FIELD_HELP = {
  category:
    "Filter the timeline to one event family. Use the info icons in the dropdown area or row badges for per-category detail.",
  card: "Show events correlated with a Plane card (RPG-N). Matches correlation.card or correlation_id.",
  run_id: "Filter by observer run id — matches correlation.run_id or correlation_id substring.",
  event_type: "Substring filter on event_type (e.g. gateway.shell_denied).",
} as const;

export const CORRELATION_FIELD_HELP: Record<string, string> = {
  correlation_id: "Stable key linking gateway, handoff, gate, and obs events for one workflow moment.",
  card: "Active Plane work item (RPG-N) when the event was recorded.",
  run_id: "Observer pipeline run identifier for token/cost metrics.",
  branch: "Git feature branch tied to the open SDLC gate, when present.",
  session_id: "Cursor session identifier when emitted by hooks or observer.",
};

export function describeEventType(eventType: string): string {
  return (
    EVENT_TYPE_HELP[eventType] ??
    `Studio event "${eventType}". Open the payload below for structured fields.`
  );
}

export function describeCategory(category: EventCategory): CategoryHelp {
  return CATEGORY_HELP[category];
}
