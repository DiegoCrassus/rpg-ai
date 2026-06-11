import { describe, expect, it } from "vitest";

import type { CanvasEdge, CanvasNode } from "../../types/canvas";
import {
  applyDagreLayout,
  mapCanvasEdge,
  mapCanvasNode,
  mapCanvasToFlow,
  worstValidationStatus,
} from "./mapViewModel";

const sampleNode: CanvasNode = {
  id: "display.node.stage.implementation",
  graph_node_id: "node.stage.implementation",
  label: "Implementation",
  type: "stage",
  category: "sdlc",
  source_refs: [{ ref_type: "path", ref: ".sdlc/stages/implementation.yaml" }],
  validation_overlays: [
    {
      id: "overlay.1",
      status: "pass",
      check_type: "registry",
      message_count: 0,
      source_refs: [],
    },
  ],
};

const sampleEdge: CanvasEdge = {
  id: "display.edge.1",
  graph_edge_id: "edge.1",
  source: "display.node.stage.implementation",
  target: "display.node.stage.qa",
  relation: "transitions_to",
  source_refs: [],
  validation_overlays: [],
  label: "next",
};

describe("worstValidationStatus", () => {
  it("returns not_run when no overlays", () => {
    expect(worstValidationStatus([])).toBe("not_run");
  });

  it("picks fail over warn and pass", () => {
    expect(
      worstValidationStatus([
        { id: "a", status: "pass", check_type: "x", message_count: 0, source_refs: [] },
        { id: "b", status: "fail", check_type: "y", message_count: 1, source_refs: [] },
        { id: "c", status: "warn", check_type: "z", message_count: 1, source_refs: [] },
      ]),
    ).toBe("fail");
  });
});

describe("mapCanvasNode", () => {
  it("maps API node to React Flow studioNode", () => {
    const flow = mapCanvasNode(sampleNode);
    expect(flow.id).toBe(sampleNode.id);
    expect(flow.type).toBe("studioNode");
    expect(flow.data.label).toBe("Implementation");
    expect(flow.data.validationStatus).toBe("pass");
    expect(flow.data.validationBorderVisible).toBe(true);
    expect(flow.data.authority).toBe("derived_non_authoritative");
    expect(flow.data.sourceRefs).toEqual([".sdlc/stages/implementation.yaml"]);
  });
});

describe("mapCanvasEdge", () => {
  it("maps source/target and relation label", () => {
    const edge = mapCanvasEdge(sampleEdge);
    expect(edge.source).toBe(sampleEdge.source);
    expect(edge.target).toBe(sampleEdge.target);
    expect(edge.label).toBe("next");
    expect(edge.animated).toBe(true);
  });
});

describe("applyDagreLayout", () => {
  it("assigns non-zero positions", () => {
    const nodes = [mapCanvasNode(sampleNode), mapCanvasNode({ ...sampleNode, id: "display.node.stage.qa" })];
    const edges = [mapCanvasEdge(sampleEdge)];
    const laid = applyDagreLayout(nodes, edges);
    expect(laid.nodes[0].position.x).not.toBe(0);
    expect(laid.nodes[0].position.y).not.toBe(0);
    expect(laid.nodes[1].position.y).toBeGreaterThan(laid.nodes[0].position.y);
  });
});

describe("mapCanvasToFlow", () => {
  it("returns positioned nodes and edges", () => {
    const result = mapCanvasToFlow([sampleNode], [sampleEdge]);
    expect(result.nodes).toHaveLength(1);
    expect(result.edges).toHaveLength(1);
    expect(result.nodes[0].position.x).toBeDefined();
  });
});
