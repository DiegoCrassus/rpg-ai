import type { CanvasNode } from "../../types/canvas";
import type { PipelineStageMeta } from "../../types/pipeline";

/** React Flow drag-and-drop MIME type (WB-2.1). */
export const REACT_FLOW_DRAG_MIME = "application/reactflow";

export type StageDragPayload = {
  assetType: "stage";
  stageId: string;
};

export function normalizeStageSlug(stageId: string): string {
  return stageId.replace(/^stage\./, "");
}

/** Display node id aligned with workflow builder canvas API. */
export function stageDisplayId(stageId: string): string {
  const slug = normalizeStageSlug(stageId);
  return `display.node.stage.${slug}`;
}

export function stageGraphNodeId(stageId: string): string {
  const slug = normalizeStageSlug(stageId);
  return `node.stage.${slug}`;
}

export function encodeStageDragPayload(stageId: string): string {
  const payload: StageDragPayload = { assetType: "stage", stageId };
  return JSON.stringify(payload);
}

export function parseStageDragPayload(raw: string): StageDragPayload | null {
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw) as Partial<StageDragPayload>;
    if (parsed.assetType !== "stage" || typeof parsed.stageId !== "string" || !parsed.stageId) {
      return null;
    }
    return { assetType: "stage", stageId: parsed.stageId };
  } catch {
    return null;
  }
}

export function createStageCanvasNode(stage: PipelineStageMeta): CanvasNode {
  const slug = normalizeStageSlug(stage.id);
  return {
    id: stageDisplayId(slug),
    graph_node_id: stageGraphNodeId(slug),
    label: stage.name,
    type: "stage",
    category: "sdlc",
    source_refs: [{ ref_type: "path", ref: ".sdlc/stages/lifecycle.yaml" }],
    validation_overlays: [],
  };
}

export function findStageOnCanvas(
  nodes: CanvasNode[],
  stageId: string,
): CanvasNode | undefined {
  const displayId = stageDisplayId(stageId);
  return nodes.find((node) => node.id === displayId);
}
