import type { CanvasEdge } from "../../types/canvas";
import type { PipelineAgentMeta, PipelineStageMeta } from "../../types/pipeline";
import type { DashboardSummary } from "../../types/studio";

type SessionSlice = DashboardSummary["session"];
import { normalizeStageSlug, type StageRuntimeStatus } from "../canvas/workflowRuntime";

export type WorkflowTrackId = "main" | "incident";

export type WorkflowTrackDef = {
  id: WorkflowTrackId;
  label: string;
  shortLabel: string;
  summary: string;
  stageSlugs: string[];
  relationNote: string;
};

export const WORKFLOW_TRACKS: Record<WorkflowTrackId, WorkflowTrackDef> = {
  main: {
    id: "main",
    label: "Delivery pipeline",
    shortLabel: "Delivery",
    summary:
      "Standard path from Plane ticket to merge, deploy, and observability — used for features, bugfixes, and greenfield work.",
    stageSlugs: [
      "ticket",
      "requirements",
      "architecture",
      "implementation",
      "validation",
      "review",
      "deployment",
      "observability",
    ],
    relationNote:
      "After observability, production signals may trigger the Incident track. Auto Fix reuses the same implementation gate as this pipeline's Implementation stage.",
  },
  incident: {
    id: "incident",
    label: "Incident response",
    shortLabel: "Incident",
    summary:
      "Corrective path when something breaks in production — document the incident, then prepare an automated fix.",
    stageSlugs: ["incident", "autofix"],
    relationNote:
      "Branches from normal delivery: not a step after Observability in the linear graph, but a parallel entry when ops detects failure. Auto Fix shares the implementation gate with Delivery → Implementation, then typically re-enters Validation on the main pipeline.",
  },
};

export type WorkflowStepView = {
  slug: string;
  order: number;
  name: string;
  description: string;
  agentId: string | null;
  agentName: string | null;
  runtimeStatus: StageRuntimeStatus;
  transitionLabel: string | null;
  transitionSummary: string | null;
};

export type WorkflowTrackRuntime = {
  gateOpen: boolean;
  executionActive: boolean;
  liveSource: SessionSlice["live_source"];
  activeTrackId: WorkflowTrackId | null;
  stageSlug: string | null;
  nextAgent: string | null;
  stageComplete: boolean;
  inferredStage: boolean;
  steps: WorkflowStepView[];
};

function sessionIsLive(session: DashboardSummary["session"] | undefined): boolean {
  return Boolean(session?.execution_active ?? session?.gate_open);
}

const INCIDENT_SLUGS = new Set(WORKFLOW_TRACKS.incident.stageSlugs);

export function resolveActiveTrackId(stageSlug: string | null): WorkflowTrackId | null {
  if (!stageSlug) {
    return null;
  }
  if (INCIDENT_SLUGS.has(stageSlug)) {
    return "incident";
  }
  if (WORKFLOW_TRACKS.main.stageSlugs.includes(stageSlug)) {
    return "main";
  }
  return null;
}

function stageRecord(
  stages: PipelineStageMeta[],
  slug: string,
): PipelineStageMeta | undefined {
  return stages.find((item) => normalizeStageSlug(item.id) === slug);
}

function agentForStage(
  agents: PipelineAgentMeta[],
  slug: string,
): PipelineAgentMeta | undefined {
  return agents.find((agent) =>
    agent.stages.some((stage) => normalizeStageSlug(stage) === slug),
  );
}

function outgoingTransition(
  edges: CanvasEdge[],
  slug: string,
  track: WorkflowTrackDef,
): CanvasEdge | null {
  const sourceId = `display.node.stage.${slug}`;
  const outgoing = edges.filter((edge) => edge.source === sourceId);
  if (outgoing.length === 0) {
    return null;
  }
  const nextSlug = track.stageSlugs[track.stageSlugs.indexOf(slug) + 1];
  if (!nextSlug) {
    return outgoing[0];
  }
  const targetId = `display.node.stage.${nextSlug}`;
  return outgoing.find((edge) => edge.target === targetId) ?? outgoing[0];
}

export function buildTrackRuntime(
  track: WorkflowTrackDef,
  session: DashboardSummary["session"] | undefined,
  stages: PipelineStageMeta[],
  agents: PipelineAgentMeta[],
  edges: CanvasEdge[],
): WorkflowTrackRuntime {
  const gateOpen = Boolean(session?.gate_open);
  const executionActive = sessionIsLive(session);
  const stageSlug = normalizeStageSlug(session?.stage);
  const nextAgent = session?.next_agent?.trim() || null;
  const stageComplete = session?.stage_complete?.trim().toLowerCase() === "yes";
  const activeTrackId = executionActive ? resolveActiveTrackId(stageSlug) : null;
  const inThisTrack = Boolean(stageSlug && track.stageSlugs.includes(stageSlug));
  const currentIndex = stageSlug ? track.stageSlugs.indexOf(stageSlug) : -1;

  const steps: WorkflowStepView[] = track.stageSlugs.map((slug, index) => {
    const meta = stageRecord(stages, slug);
    const agent = agentForStage(agents, slug);
    const transition = outgoingTransition(edges, slug, track);

    let runtimeStatus: StageRuntimeStatus = "inactive";
    if (executionActive && inThisTrack && currentIndex >= 0) {
      if (index === currentIndex) {
        runtimeStatus = "current";
      } else if (index < currentIndex) {
        runtimeStatus = "completed";
      } else {
        runtimeStatus = "upcoming";
      }
    }

    return {
      slug,
      order: index + 1,
      name: meta?.name ?? slug,
      description: meta?.description ?? "",
      agentId: agent?.id ?? null,
      agentName: agent?.name ?? null,
      runtimeStatus,
      transitionLabel: transition?.label ?? null,
      transitionSummary: transition?.summary ?? null,
    };
  });

  return {
    gateOpen,
    executionActive,
    liveSource: session?.live_source ?? (gateOpen ? "gate" : null),
    activeTrackId,
    stageSlug: inThisTrack ? stageSlug : null,
    nextAgent: inThisTrack ? nextAgent : null,
    stageComplete: inThisTrack ? stageComplete : false,
    inferredStage: Boolean(session?.inferred_stage),
    steps,
  };
}

export function crossTrackRelation(
  viewingTrackId: WorkflowTrackId,
  activeTrackId: WorkflowTrackId | null,
): string {
  if (!activeTrackId) {
    return WORKFLOW_TRACKS[viewingTrackId].relationNote;
  }
  if (viewingTrackId === activeTrackId) {
    return WORKFLOW_TRACKS[viewingTrackId].relationNote;
  }
  const active = WORKFLOW_TRACKS[activeTrackId];
  const viewing = WORKFLOW_TRACKS[viewingTrackId];
  return `Session is running on ${active.label} (${active.shortLabel}). You are previewing ${viewing.label}. ${viewing.relationNote}`;
}
