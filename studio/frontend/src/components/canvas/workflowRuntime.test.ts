import { describe, expect, it } from "vitest";

import type { CanvasEdge, CanvasNode } from "../../types/canvas";
import {
  nodeIdToStageSlug,
  resolveWorkflowRuntime,
  stageSlugToNodeId,
} from "./workflowRuntime";

const stages = [
  { id: "ticket", name: "Ticket", order: 1 },
  { id: "requirements", name: "Requirements", order: 2 },
  { id: "implementation", name: "Implementation", order: 4 },
];

const nodes: CanvasNode[] = stages.map((stage) => ({
  id: stageSlugToNodeId(stage.id),
  graph_node_id: `node.stage.${stage.id}`,
  label: stage.name,
  type: "stage",
  category: "sdlc",
  source_refs: [],
  validation_overlays: [],
}));

const edges: CanvasEdge[] = [
  {
    id: "edge.ticket_req",
    graph_edge_id: "transition.ticket_to_requirements",
    source: stageSlugToNodeId("ticket"),
    target: stageSlugToNodeId("requirements"),
    relation: "transitions_to",
    source_refs: [],
    validation_overlays: [],
    agent: "planner",
  },
  {
    id: "edge.req_impl",
    graph_edge_id: "transition.requirements_to_implementation",
    source: stageSlugToNodeId("requirements"),
    target: stageSlugToNodeId("implementation"),
    relation: "transitions_to",
    source_refs: [],
    validation_overlays: [],
    agent: "implementer",
  },
];

describe("workflowRuntime", () => {
  it("maps stage slug to display node id", () => {
    expect(stageSlugToNodeId("implementation")).toBe("display.node.stage.implementation");
    expect(stageSlugToNodeId("stage.implementation")).toBe("display.node.stage.implementation");
    expect(nodeIdToStageSlug("display.node.stage.ticket")).toBe("ticket");
  });

  it("marks completed, current, and upcoming nodes when gate is open", () => {
    const runtime = resolveWorkflowRuntime(
      {
        gate_open: true,
        card: "INVES-1",
        stage: "requirements",
        next_agent: "planner",
        stage_complete: "no",
      },
      nodes,
      edges,
      stages,
    );

    expect(runtime.currentNodeId).toBe(stageSlugToNodeId("requirements"));
    expect(runtime.nodeStatusById[stageSlugToNodeId("ticket")]).toBe("completed");
    expect(runtime.nodeStatusById[stageSlugToNodeId("requirements")]).toBe("current");
    expect(runtime.nodeStatusById[stageSlugToNodeId("implementation")]).toBe("upcoming");
    expect(runtime.activeEdgeId).toBe("edge.req_impl");
  });

  it("returns inactive nodes when gate is closed", () => {
    const runtime = resolveWorkflowRuntime(
      { gate_open: false, stage: "implementation" },
      nodes,
      edges,
      stages,
    );
    expect(runtime.currentNodeId).toBe(stageSlugToNodeId("implementation"));
    expect(runtime.nodeStatusById[stageSlugToNodeId("ticket")]).toBe("inactive");
  });
});
