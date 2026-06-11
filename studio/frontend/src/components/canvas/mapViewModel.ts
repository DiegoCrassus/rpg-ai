import dagre from "@dagrejs/dagre";
import type { Edge, Node } from "@xyflow/react";

import type {
  CanvasEdge,
  CanvasNode,
  ValidationOverlaySummary,
  ValidationStatus,
} from "../../types/canvas";
import type { StageRuntimeStatus } from "./workflowRuntime";

export const AUTHORITY = "derived_non_authoritative";

const STATUS_RANK: Record<ValidationStatus, number> = {
  fail: 0,
  warn: 1,
  not_run: 2,
  pass: 3,
};

export type StudioNodeData = {
  label: string;
  category: string;
  entityType: string;
  graphNodeId: string;
  validationStatus: ValidationStatus;
  validationBorderVisible: boolean;
  runtimeStatus?: StageRuntimeStatus;
  sourceRefs: string[];
  authority: typeof AUTHORITY;
};

export function worstValidationStatus(
  overlays: ValidationOverlaySummary[] | undefined,
): ValidationStatus {
  if (!overlays?.length) {
    return "not_run";
  }
  return overlays.reduce<ValidationStatus>((worst, overlay) => {
    return STATUS_RANK[overlay.status] < STATUS_RANK[worst] ? overlay.status : worst;
  }, "pass");
}

export function mapCanvasNode(node: CanvasNode): Node<StudioNodeData> {
  return {
    id: node.id,
    type: "studioNode",
    position: { x: 0, y: 0 },
    data: {
      label: node.label,
      category: node.category,
      entityType: node.type,
      graphNodeId: node.graph_node_id,
      validationStatus: worstValidationStatus(node.validation_overlays),
      validationBorderVisible: true,
      sourceRefs: node.source_refs.map((ref) => ref.ref),
      authority: AUTHORITY,
    },
  };
}

export function mapCanvasEdge(edge: CanvasEdge, options?: { useWorkflowEdge?: boolean }): Edge {
  const useWorkflowEdge = options?.useWorkflowEdge ?? false;
  return {
    id: edge.id,
    source: edge.source,
    target: edge.target,
    type: useWorkflowEdge ? "workflowTransition" : "smoothstep",
    label: edge.label ?? edge.relation,
    animated: edge.relation === "transitions_to",
    data: {
      relation: edge.relation,
      graphEdgeId: edge.graph_edge_id,
      agent: edge.agent ?? undefined,
      skill: edge.skill ?? undefined,
      label: edge.label ?? undefined,
    },
  };
}

export function mapCanvasToFlow(
  nodes: CanvasNode[],
  edges: CanvasEdge[],
  options?: { useWorkflowEdge?: boolean },
) {
  const flowNodes = nodes.map(mapCanvasNode);
  const flowEdges = edges.map((edge) => mapCanvasEdge(edge, options));
  return applyDagreLayout(flowNodes, flowEdges);
}

const NODE_WIDTH = 220;
const NODE_HEIGHT = 72;

export function applyDagreLayout(
  nodes: Node<StudioNodeData>[],
  edges: Edge[],
): { nodes: Node<StudioNodeData>[]; edges: Edge[] } {
  if (nodes.length === 0) {
    return { nodes, edges };
  }

  const graph = new dagre.graphlib.Graph();
  graph.setDefaultEdgeLabel(() => ({}));
  graph.setGraph({ rankdir: "TB", nodesep: 60, ranksep: 90, marginx: 24, marginy: 24 });

  for (const node of nodes) {
    graph.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  }
  for (const edge of edges) {
    graph.setEdge(edge.source, edge.target);
  }

  dagre.layout(graph);

  const positioned = nodes.map((node) => {
    const layout = graph.node(node.id);
    if (!layout) {
      return node;
    }
    return {
      ...node,
      position: {
        x: layout.x - NODE_WIDTH / 2,
        y: layout.y - NODE_HEIGHT / 2,
      },
    };
  });

  return { nodes: positioned, edges };
}

export function validationStatusColor(status: ValidationStatus): string {
  switch (status) {
    case "pass":
      return "#34d399";
    case "warn":
      return "#fbbf24";
    case "fail":
      return "#f87171";
    default:
      return "#64748b";
  }
}
