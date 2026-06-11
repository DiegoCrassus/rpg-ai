import type { Node, XYPosition } from "@xyflow/react";

import type { CanvasNode } from "../../types/canvas";
import type { PipelineAgentMeta, PipelineGateMeta } from "../../types/pipeline";
import { stageSlugFromGraphNodeId } from "./workflowDraft";

export const AGENT_ANNOTATION_OFFSET: XYPosition = { x: 260, y: 0 };
export const GATE_ANNOTATION_OFFSET: XYPosition = { x: -200, y: 0 };

export type AgentAnnotationNodeData = {
  agentId: string;
  agentName: string;
  skillName: string;
  linkedStages: string[];
};

export type GateAnnotationNodeData = {
  gateId: string;
  gateName: string;
  stage: string;
  allowedPrefixCount: number;
  sourceRef: string;
};

export type BuilderAnnotationNodeData = AgentAnnotationNodeData | GateAnnotationNodeData;

export function isAgentAnnotationNode(node: CanvasNode): boolean {
  return node.type === "agent_annotation";
}

export function isGateAnnotationNode(node: CanvasNode): boolean {
  return node.type === "gate_annotation";
}

export function isAnnotationCanvasNode(node: CanvasNode): boolean {
  return isAgentAnnotationNode(node) || isGateAnnotationNode(node);
}

export function agentAnnotationId(agentId: string): string {
  return `display.annotation.agent.${agentId}`;
}

export function gateAnnotationId(gateId: string): string {
  return `display.annotation.gate.${gateId}`;
}

function stagePositionBySlug(
  stageNodes: Array<Node<{ graphNodeId: string }>>,
): Map<string, XYPosition> {
  const positions = new Map<string, XYPosition>();
  for (const node of stageNodes) {
    const slug = stageSlugFromGraphNodeId(node.data.graphNodeId);
    positions.set(slug, node.position);
  }
  return positions;
}

export function buildAgentAnnotationNodes(
  agents: PipelineAgentMeta[],
  stageFlowNodes: Array<Node<{ graphNodeId: string }>>,
): Node<AgentAnnotationNodeData>[] {
  const stagePositions = stagePositionBySlug(stageFlowNodes);
  const nodes: Node<AgentAnnotationNodeData>[] = [];

  agents.forEach((agent, index) => {
    const anchorStage = agent.stages[0];
    if (!anchorStage) {
      return;
    }
    const anchor = stagePositions.get(anchorStage);
    if (!anchor) {
      return;
    }

    nodes.push({
      id: agentAnnotationId(agent.id),
      type: "agentAnnotationNode",
      position: {
        x: anchor.x + AGENT_ANNOTATION_OFFSET.x,
        y: anchor.y + AGENT_ANNOTATION_OFFSET.y + index * 52,
      },
      connectable: false,
      selectable: true,
      draggable: false,
      data: {
        agentId: agent.id,
        agentName: agent.name,
        skillName: agent.skill.name,
        linkedStages: agent.stages,
      },
    });
  });

  return nodes;
}

export function buildGateAnnotationNodes(
  gates: PipelineGateMeta[],
  stageFlowNodes: Array<Node<{ graphNodeId: string }>>,
): Node<GateAnnotationNodeData>[] {
  const stagePositions = stagePositionBySlug(stageFlowNodes);
  const nodes: Node<GateAnnotationNodeData>[] = [];

  gates.forEach((gate, index) => {
    const anchor = stagePositions.get(gate.stage);
    if (!anchor) {
      return;
    }

    nodes.push({
      id: gateAnnotationId(gate.id),
      type: "gateAnnotationNode",
      position: {
        x: anchor.x + GATE_ANNOTATION_OFFSET.x,
        y: anchor.y + GATE_ANNOTATION_OFFSET.y + index * 52,
      },
      connectable: false,
      selectable: true,
      draggable: false,
      data: {
        gateId: gate.id,
        gateName: gate.name,
        stage: gate.stage,
        allowedPrefixCount: gate.allowed_prefixes.length,
        sourceRef: gate.source_ref,
      },
    });
  });

  return nodes;
}

export function annotationNodesForExport(nodes: CanvasNode[]): CanvasNode[] {
  return nodes.filter((node) => !isAnnotationCanvasNode(node));
}
