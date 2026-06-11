import { describe, expect, it } from "vitest";

import {
  collectBrokenRefIndex,
  mapRegistryGraphToCanvas,
  pathLabelChipClass,
  scenarioSlugFromId,
} from "./registryViewModel";
import type { RegistryGraphResponse } from "../../types/foundation";

const sampleGraph: RegistryGraphResponse = {
  graph: { id: "graph.sdlc_studio.registry" },
  nodes: [
    {
      id: "node.a",
      type: "agent",
      category: "cursor",
      label: "A",
      source_refs: [{ ref_type: "path", ref: ".cursor/agents/a.md" }],
    },
    {
      id: "node.b",
      type: "skill",
      category: "cursor",
      label: "B",
      source_refs: [{ ref_type: "path", ref: "missing/path.md" }],
    },
  ],
  edges: [
    {
      id: "edge.rel.a.uses.b",
      from: "node.a",
      to: "node.b",
      relation: "uses",
      source_refs: [],
    },
  ],
  broken_refs: {
    unresolved_relationships: [{ id: "edge.rel.a.uses.b", detail: "unresolved" }],
    missing_optional_source_paths: [{ id: "missing/path.md", detail: "missing" }],
  },
  summary: { broken_ref_count: 2 },
};

describe("registryViewModel", () => {
  it("marks broken nodes and edges from API broken_refs", () => {
    const broken = collectBrokenRefIndex(
      sampleGraph.broken_refs,
      sampleGraph.nodes,
      sampleGraph.edges,
    );
    expect(broken.brokenEdgeIds.has("edge.rel.a.uses.b")).toBe(true);
    expect(broken.brokenNodeIds.has("node.a")).toBe(true);
    expect(broken.brokenNodeIds.has("node.b")).toBe(true);
    expect(broken.panelItems).toHaveLength(2);
  });

  it("maps registry graph to canvas nodes with fail overlays", () => {
    const { nodes, edges } = mapRegistryGraphToCanvas(sampleGraph);
    expect(nodes.find((node) => node.id === "node.b")?.validation_overlays[0]?.status).toBe(
      "fail",
    );
    expect(edges[0]?.validation_overlays[0]?.status).toBe("fail");
  });

  it("derives scenario slug from API id", () => {
    expect(scenarioSlugFromId("simulation.scenario.docs_only")).toBe("docs_only");
  });

  it("maps path label to chip classes", () => {
    expect(pathLabelChipClass("expected")).toContain("emerald");
    expect(pathLabelChipClass("unsupported")).toContain("amber");
  });
});
