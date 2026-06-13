import { describe, expect, it } from "vitest";

import type { CanvasEdge, CanvasNode } from "../../types/canvas";
import {
  buildWorkflowProposalRequest,
  createTransitionDraft,
  draftsFromCanvas,
  draftsToCanvasEdges,
  serializeTransitionsYaml,
  stageSlugFromGraphNodeId,
  transitionIdFromGraphEdgeId,
  WORKFLOW_TARGET_PATH,
} from "./workflowDraft";

const stageNode = (id: string, graphNodeId: string, label: string): CanvasNode => ({
  id,
  graph_node_id: graphNodeId,
  label,
  type: "stage",
  category: "sdlc",
  source_refs: [],
  validation_overlays: [],
});

const transitionEdge = (
  id: string,
  graphEdgeId: string,
  source: string,
  target: string,
  label?: string,
): CanvasEdge => ({
  id,
  graph_edge_id: graphEdgeId,
  source,
  target,
  relation: "transitions_to",
  source_refs: [],
  validation_overlays: [],
  label,
});

describe("stageSlugFromGraphNodeId", () => {
  it("extracts stage slug from node.stage ids", () => {
    expect(stageSlugFromGraphNodeId("node.stage.implementation")).toBe("implementation");
  });

  it("falls back to last segment", () => {
    expect(stageSlugFromGraphNodeId("artifact.custom")).toBe("custom");
  });
});

describe("transitionIdFromGraphEdgeId", () => {
  it("parses edge.transition prefix", () => {
    expect(transitionIdFromGraphEdgeId("edge.transition.architecture_to_implementation", "", "")).toBe(
      "architecture_to_implementation",
    );
  });

  it("builds id from stages when edge id is unknown", () => {
    expect(transitionIdFromGraphEdgeId("edge.unknown", "a", "b")).toBe("a_to_b");
  });
});

describe("draftsFromCanvas", () => {
  it("maps transitions_to edges to workflow drafts", () => {
    const nodes = [
      stageNode("display.node.a", "node.stage.architecture", "Architecture"),
      stageNode("display.node.b", "node.stage.implementation", "Implementation"),
    ];
    const edges = [
      transitionEdge(
        "display.edge.1",
        "edge.transition.architecture_to_implementation",
        "display.node.a",
        "display.node.b",
        "Architecture → Implementation",
      ),
    ];

    const drafts = draftsFromCanvas(nodes, edges);
    expect(drafts).toHaveLength(1);
    expect(drafts[0]).toMatchObject({
      id: "architecture_to_implementation",
      from_stage: "architecture",
      to_stage: "implementation",
      name: "Architecture → Implementation",
      edgeDisplayId: "display.edge.1",
    });
  });

  it("ignores non-transition edges", () => {
    const nodes = [stageNode("display.node.a", "node.stage.a", "A")];
    const edges: CanvasEdge[] = [
      {
        id: "e1",
        graph_edge_id: "edge.ref.1",
        source: "display.node.a",
        target: "display.node.a",
        relation: "references",
        source_refs: [],
        validation_overlays: [],
      },
    ];
    expect(draftsFromCanvas(nodes, edges)).toHaveLength(0);
  });
});

describe("serializeTransitionsYaml", () => {
  it("emits version header and workflow entries", () => {
    const yaml = serializeTransitionsYaml([
      {
        id: "a_to_b",
        name: "A → B",
        from_stage: "a",
        to_stage: "b",
        description: "Test transition",
        agent: "implementer",
        skill: "implementation",
        preconditions: ["Ready"],
        outputs: ["Done"],
        edgeDisplayId: "e1",
        sourceDisplayId: "n1",
        targetDisplayId: "n2",
      },
    ]);

    expect(yaml).toContain("version: '1.0'");
    expect(yaml).toContain("workflows:");
    expect(yaml).toContain("- id: a_to_b");
    expect(yaml).toContain('name: "A → B"');
    expect(yaml).toContain("  - Ready");
  });
});

describe("buildWorkflowProposalRequest", () => {
  it("targets transitions.yaml with replace_block op", () => {
    const request = buildWorkflowProposalRequest(
      [
        {
          id: "x_to_y",
          name: "X → Y",
          from_stage: "x",
          to_stage: "y",
          description: "",
          agent: "qa",
          skill: "qa-validation",
          preconditions: [],
          outputs: [],
          edgeDisplayId: "e",
          sourceDisplayId: "s",
          targetDisplayId: "t",
        },
      ],
      "Adjust workflow",
      "RPG-85",
    );

    expect(request.kind).toBe("workflow");
    expect(request.target_paths).toEqual([WORKFLOW_TARGET_PATH]);
    expect(request.ops[0].op).toBe("replace_block");
    expect(request.simulated_gate).toEqual({ stage: "architecture", card: "RPG-85" });
  });
});

describe("draftsToCanvasEdges", () => {
  it("includes agent and skill on transition edges", () => {
    const edges = draftsToCanvasEdges([
      {
        id: "a_to_b",
        name: "A → B",
        from_stage: "a",
        to_stage: "b",
        description: "",
        agent: "architect",
        skill: "architecture-analysis",
        preconditions: [],
        outputs: [],
        edgeDisplayId: "e1",
        sourceDisplayId: "n1",
        targetDisplayId: "n2",
      },
    ]);

    expect(edges[0]).toMatchObject({
      agent: "architect",
      skill: "architecture-analysis",
    });
  });
});

describe("createTransitionDraft", () => {
  it("builds a draft from connected stage nodes", () => {
    const nodes = new Map([
      ["n1", stageNode("n1", "node.stage.planning", "Planning")],
      ["n2", stageNode("n2", "node.stage.architecture", "Architecture")],
    ]);
    const draft = createTransitionDraft("n1", "n2", nodes);
    expect(draft).toMatchObject({
      from_stage: "planning",
      to_stage: "architecture",
      id: "planning_to_architecture",
    });
  });
});
