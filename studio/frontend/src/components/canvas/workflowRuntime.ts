import type { CanvasEdge, CanvasNode } from "../../types/canvas";
import type { DashboardSummary } from "../../types/studio";
import type { PipelineStageMeta } from "../../types/pipeline";

export type StageRuntimeStatus = "current" | "completed" | "upcoming" | "inactive";

export type WorkflowRuntimeState = {
  gateOpen: boolean;
  stageSlug: string | null;
  currentNodeId: string | null;
  nextAgent: string | null;
  stageComplete: boolean;
  activeEdgeId: string | null;
  nodeStatusById: Record<string, StageRuntimeStatus>;
};

export function normalizeStageSlug(stage?: string | null): string | null {
  if (!stage?.trim()) {
    return null;
  }
  return stage.trim().replace(/^stage\./, "");
}

export function stageSlugToNodeId(slug: string): string {
  const normalized = normalizeStageSlug(slug) ?? slug;
  return `display.node.stage.${normalized}`;
}

export function nodeIdToStageSlug(nodeId: string): string | null {
  const match = /^display\.node\.stage\.(.+)$/.exec(nodeId);
  return match?.[1] ?? null;
}

function stageOrderMap(stages: PipelineStageMeta[]): Map<string, number> {
  const map = new Map<string, number>();
  for (const stage of stages) {
    const slug = normalizeStageSlug(stage.id);
    if (slug) {
      map.set(slug, stage.order ?? 999);
    }
  }
  return map;
}

function findOutgoingEdge(
  edges: CanvasEdge[],
  currentNodeId: string,
  nextAgent?: string | null,
): CanvasEdge | null {
  const outgoing = edges.filter((edge) => edge.source === currentNodeId);
  if (outgoing.length === 0) {
    return null;
  }
  if (!nextAgent?.trim()) {
    return outgoing[0];
  }
  const agentNeedle = nextAgent.trim().toLowerCase();
  const byAgent = outgoing.find((edge) => edge.agent?.toLowerCase() === agentNeedle);
  return byAgent ?? outgoing[0];
}

export function resolveWorkflowRuntime(
  session: DashboardSummary["session"] | undefined,
  nodes: CanvasNode[],
  edges: CanvasEdge[],
  pipelineStages: PipelineStageMeta[],
): WorkflowRuntimeState {
  const gateOpen = Boolean(session?.gate_open);
  const stageSlug = normalizeStageSlug(session?.stage);
  const nextAgent = session?.next_agent?.trim() || null;
  const stageComplete = session?.stage_complete?.trim().toLowerCase() === "yes";
  const orderBySlug = stageOrderMap(pipelineStages);
  const currentOrder = stageSlug ? orderBySlug.get(stageSlug) : undefined;

  const nodeStatusById: Record<string, StageRuntimeStatus> = {};
  for (const node of nodes) {
    const slug = nodeIdToStageSlug(node.id);
    if (!slug) {
      nodeStatusById[node.id] = "inactive";
      continue;
    }
    const order = orderBySlug.get(slug);
    if (!gateOpen || !stageSlug || order === undefined || currentOrder === undefined) {
      nodeStatusById[node.id] = "inactive";
      continue;
    }
    if (slug === stageSlug) {
      nodeStatusById[node.id] = "current";
    } else if (order < currentOrder) {
      nodeStatusById[node.id] = "completed";
    } else {
      nodeStatusById[node.id] = "upcoming";
    }
  }

  const currentNodeId = stageSlug ? stageSlugToNodeId(stageSlug) : null;
  const activeEdge =
    gateOpen && currentNodeId && !stageComplete
      ? findOutgoingEdge(edges, currentNodeId, nextAgent)
      : null;

  return {
    gateOpen,
    stageSlug,
    currentNodeId,
    nextAgent,
    stageComplete,
    activeEdgeId: activeEdge?.id ?? null,
    nodeStatusById,
  };
}
