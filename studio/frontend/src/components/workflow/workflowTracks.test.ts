import { describe, expect, it } from "vitest";

import type { CanvasEdge } from "../../types/canvas";
import {
  buildTrackRuntime,
  resolveActiveTrackId,
  WORKFLOW_TRACKS,
} from "./workflowTracks";

const stages = [
  { id: "ticket", name: "Ticket", order: 1, description: "Capture work" },
  { id: "implementation", name: "Implementation", order: 4, description: "Code" },
  { id: "incident", name: "Incident", order: 9, description: "Ops issue" },
  { id: "autofix", name: "Auto Fix", order: 10, description: "Fix" },
];

const agents = [
  {
    id: "planner",
    name: "Planner",
    stages: ["ticket", "requirements"],
    cursor_agent: ".cursor/agents/planner.md",
    skill: { id: "x", name: "X" },
  },
  {
    id: "implementer",
    name: "Implementer",
    stages: ["implementation", "autofix"],
    cursor_agent: ".cursor/agents/implementer.md",
    skill: { id: "y", name: "Y" },
  },
];

const edges: CanvasEdge[] = [
  {
    id: "e1",
    graph_edge_id: "t1",
    source: "display.node.stage.ticket",
    target: "display.node.stage.requirements",
    relation: "transitions_to",
    source_refs: [],
    validation_overlays: [],
    label: "Ticket → Requirements",
    agent: "planner",
  },
  {
    id: "e2",
    graph_edge_id: "t2",
    source: "display.node.stage.incident",
    target: "display.node.stage.autofix",
    relation: "transitions_to",
    source_refs: [],
    validation_overlays: [],
    label: "Incident → Auto Fix",
    agent: "implementer",
  },
];

describe("workflowTracks", () => {
  it("resolves active track from session stage", () => {
    expect(resolveActiveTrackId("implementation")).toBe("main");
    expect(resolveActiveTrackId("incident")).toBe("incident");
    expect(resolveActiveTrackId("autofix")).toBe("incident");
  });

  it("marks only the viewed track steps as live", () => {
    const main = buildTrackRuntime(
      WORKFLOW_TRACKS.main,
      {
        gate_open: true,
        execution_active: true,
        stage: "implementation",
        next_agent: "implementer",
      },
      stages,
      agents,
      edges,
    );
    expect(main.executionActive).toBe(true);
    expect(main.activeTrackId).toBe("main");
    expect(main.steps.find((s) => s.slug === "implementation")?.runtimeStatus).toBe("current");
    expect(main.steps.find((s) => s.slug === "ticket")?.runtimeStatus).toBe("completed");

    const incident = buildTrackRuntime(
      WORKFLOW_TRACKS.incident,
      {
        gate_open: true,
        execution_active: true,
        stage: "implementation",
        next_agent: "implementer",
      },
      stages,
      agents,
      edges,
    );
    expect(incident.steps.every((s) => s.runtimeStatus === "inactive")).toBe(true);
  });

  it("treats execution_active without gate_open as live", () => {
    const main = buildTrackRuntime(
      WORKFLOW_TRACKS.main,
      {
        gate_open: false,
        execution_active: true,
        live_source: "handoff",
        stage: "ticket",
        next_agent: "planner",
        inferred_stage: true,
      },
      stages,
      agents,
      edges,
    );
    expect(main.executionActive).toBe(true);
    expect(main.steps.find((s) => s.slug === "ticket")?.runtimeStatus).toBe("current");
  });

  it("highlights incident track when session is on incident", () => {
    const incident = buildTrackRuntime(
      WORKFLOW_TRACKS.incident,
      {
        gate_open: true,
        execution_active: true,
        stage: "incident",
        next_agent: "implementer",
      },
      stages,
      agents,
      edges,
    );
    expect(incident.activeTrackId).toBe("incident");
    expect(incident.steps[0].runtimeStatus).toBe("current");
    expect(incident.steps[1].runtimeStatus).toBe("upcoming");
  });
});
