import { describe, expect, it } from "vitest";

import {
  createStageCanvasNode,
  encodeStageDragPayload,
  findStageOnCanvas,
  parseStageDragPayload,
  stageDisplayId,
  stageGraphNodeId,
} from "./builderDnD";

describe("builderDnD", () => {
  it("builds display and graph ids from pipeline slug", () => {
    expect(stageDisplayId("implementation")).toBe("display.node.stage.implementation");
    expect(stageGraphNodeId("implementation")).toBe("node.stage.implementation");
  });

  it("normalizes stage.* ids", () => {
    expect(stageDisplayId("stage.validation")).toBe("display.node.stage.validation");
  });

  it("round-trips drag payload", () => {
    const raw = encodeStageDragPayload("architecture");
    expect(parseStageDragPayload(raw)).toEqual({
      assetType: "stage",
      stageId: "architecture",
    });
  });

  it("rejects invalid drag payload", () => {
    expect(parseStageDragPayload("")).toBeNull();
    expect(parseStageDragPayload("{}")).toBeNull();
    expect(parseStageDragPayload('{"assetType":"agent"}')).toBeNull();
  });

  it("creates canvas node aligned with backend", () => {
    const node = createStageCanvasNode({
      id: "implementation",
      name: "Implementation",
      description: "",
    });
    expect(node).toMatchObject({
      id: "display.node.stage.implementation",
      graph_node_id: "node.stage.implementation",
      label: "Implementation",
      type: "stage",
    });
  });

  it("finds stage on canvas by slug or prefixed id", () => {
    const nodes = [
      createStageCanvasNode({ id: "validation", name: "Validation", description: "" }),
    ];
    expect(findStageOnCanvas(nodes, "validation")?.id).toBe("display.node.stage.validation");
    expect(findStageOnCanvas(nodes, "stage.architecture")).toBeUndefined();
  });
});
