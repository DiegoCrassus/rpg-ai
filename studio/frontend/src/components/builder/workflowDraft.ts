import type { CanvasEdge, CanvasNode } from "../../types/canvas";
import type { WorkflowTransitionDraft } from "../../types/builder";
import type { ProposalCreateRequest } from "../../types/proposals";

export const WORKFLOW_TARGET_PATH = ".sdlc/workflows/transitions.yaml";

export function stageSlugFromGraphNodeId(graphNodeId: string): string {
  const match = graphNodeId.match(/^node\.stage\.(.+)$/);
  if (match) {
    return match[1];
  }
  const parts = graphNodeId.split(".");
  return parts[parts.length - 1] || graphNodeId;
}

export function transitionIdFromGraphEdgeId(
  graphEdgeId: string,
  fromStage: string,
  toStage: string,
): string {
  const match = graphEdgeId.match(/^edge\.(?:transition|workflow)\.(.+)$/);
  if (match) {
    return match[1];
  }
  if (fromStage && toStage) {
    return `${fromStage}_to_${toStage}`;
  }
  return graphEdgeId.replace(/^edge\./, "").replace(/\./g, "_");
}

export function draftsFromCanvas(
  nodes: CanvasNode[],
  edges: CanvasEdge[],
): WorkflowTransitionDraft[] {
  const nodeById = new Map(nodes.map((node) => [node.id, node]));

  return edges
    .filter((edge) => edge.relation === "transitions_to")
    .map((edge) => {
      const fromNode = nodeById.get(edge.source);
      const toNode = nodeById.get(edge.target);
      const fromStage = stageSlugFromGraphNodeId(fromNode?.graph_node_id ?? edge.source);
      const toStage = stageSlugFromGraphNodeId(toNode?.graph_node_id ?? edge.target);
      const id = transitionIdFromGraphEdgeId(edge.graph_edge_id, fromStage, toStage);

      return {
        id,
        name: edge.label ?? `${fromStage} → ${toStage}`,
        from_stage: fromStage,
        to_stage: toStage,
        description: edge.summary ?? "",
        agent: edge.agent?.trim() || "implementer",
        skill: edge.skill?.trim() || "implementation",
        preconditions: [],
        outputs: [],
        edgeDisplayId: edge.id,
        sourceDisplayId: edge.source,
        targetDisplayId: edge.target,
      };
    });
}

function yamlScalar(value: string): string {
  if (!value) {
    return '""';
  }
  if (/[:#'"\n&*!?|>[\]{}]|^\s|\s$/.test(value) || value.includes("→")) {
    return `"${value.replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
  }
  return value;
}

function yamlList(key: string, items: string[], indent: string): string[] {
  if (items.length === 0) {
    return [`${indent}${key}: []`];
  }
  return [
    `${indent}${key}:`,
    ...items.map((item) => `${indent}  - ${yamlScalar(item)}`),
  ];
}

function serializeWorkflow(draft: WorkflowTransitionDraft): string[] {
  const indent = "  ";
  const lines = [
    `${indent}- id: ${yamlScalar(draft.id)}`,
    `${indent}  name: ${yamlScalar(draft.name)}`,
    `${indent}  from_stage: ${yamlScalar(draft.from_stage)}`,
    `${indent}  to_stage: ${yamlScalar(draft.to_stage)}`,
    `${indent}  description: ${yamlScalar(draft.description)}`,
    ...yamlList("preconditions", draft.preconditions, `${indent}  `),
    `${indent}  agent: ${yamlScalar(draft.agent)}`,
    `${indent}  skill: ${yamlScalar(draft.skill)}`,
    ...yamlList("outputs", draft.outputs, `${indent}  `),
  ];
  return lines;
}

export function serializeTransitionsYaml(drafts: WorkflowTransitionDraft[]): string {
  const header = [
    "version: '1.0'",
    "description: Executable workflows linking SDLC stages.",
    "workflows:",
  ];
  const body = drafts.flatMap((draft) => serializeWorkflow(draft));
  return [...header, ...body, ""].join("\n");
}

export function buildWorkflowProposalRequest(
  drafts: WorkflowTransitionDraft[],
  title: string,
  card: string,
): ProposalCreateRequest {
  return {
    kind: "workflow",
    title,
    target_paths: [WORKFLOW_TARGET_PATH],
    ops: [
      {
        op: "replace_block",
        path: WORKFLOW_TARGET_PATH,
        content: serializeTransitionsYaml(drafts),
      },
    ],
    simulated_gate: { stage: "architecture", card },
  };
}

export function createTransitionDraft(
  sourceDisplayId: string,
  targetDisplayId: string,
  nodesById: Map<string, CanvasNode>,
): WorkflowTransitionDraft | null {
  const fromNode = nodesById.get(sourceDisplayId);
  const toNode = nodesById.get(targetDisplayId);
  if (!fromNode || !toNode) {
    return null;
  }

  const fromStage = stageSlugFromGraphNodeId(fromNode.graph_node_id);
  const toStage = stageSlugFromGraphNodeId(toNode.graph_node_id);
  const id = `${fromStage}_to_${toStage}`;

  return {
    id,
    name: `${fromNode.label} → ${toNode.label}`,
    from_stage: fromStage,
    to_stage: toStage,
    description: "",
    agent: "implementer",
    skill: "implementation",
    preconditions: [],
    outputs: [],
    edgeDisplayId: `draft.edge.${id}`,
    sourceDisplayId,
    targetDisplayId,
  };
}

export function draftsToCanvasEdges(drafts: WorkflowTransitionDraft[]): CanvasEdge[] {
  return drafts.map((draft) => ({
    id: draft.edgeDisplayId,
    graph_edge_id: `edge.transition.${draft.id}`,
    source: draft.sourceDisplayId,
    target: draft.targetDisplayId,
    relation: "transitions_to",
    source_refs: [{ ref_type: "path", ref: WORKFLOW_TARGET_PATH }],
    validation_overlays: [],
    label: draft.name,
    summary: draft.description,
    agent: draft.agent,
    skill: draft.skill,
  }));
}

export function stageNodesFromCanvas(nodes: CanvasNode[]): CanvasNode[] {
  return nodes.filter((node) => node.type === "stage");
}
