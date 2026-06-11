import { describe, expect, it } from "vitest";
import type { Node } from "@xyflow/react";

import type { CanvasNode } from "../../types/canvas";
import type { PipelineAgentMeta, PipelineGateMeta } from "../../types/pipeline";
import {
  agentAnnotationId,
  annotationNodesForExport,
  buildAgentAnnotationNodes,
  buildGateAnnotationNodes,
  gateAnnotationId,
  isAnnotationCanvasNode,
} from "./annotationNodes";

const stageFlowNode = (slug: string, x: number, y: number): Node<{ graphNodeId: string }> => ({
  id: `display.node.stage.${slug}`,
  type: "stageNode",
  position: { x, y },
  data: { graphNodeId: `node.stage.${slug}` },
});

const agentMeta = (id: string, stages: string[]): PipelineAgentMeta => ({
  id,
  name: id,
  stages,
  cursor_agent: id,
  skill: { id: `${id}-skill`, name: `${id} skill` },
});

describe("annotationNodes", () => {
  it("builds agent annotations anchored to linked stages", () => {
    const nodes = buildAgentAnnotationNodes(
      [agentMeta("architect", ["architecture"])],
      [stageFlowNode("architecture", 100, 200)],
    );

    expect(nodes).toHaveLength(1);
    expect(nodes[0].id).toBe(agentAnnotationId("architect"));
    expect(nodes[0].type).toBe("agentAnnotationNode");
    expect(nodes[0].connectable).toBe(false);
    expect(nodes[0].position.x).toBeGreaterThan(100);
  });

  it("builds gate annotations from pipeline metadata", () => {
    const gates: PipelineGateMeta[] = [
      {
        id: "implementation",
        name: "Implementation",
        stage: "implementation",
        allowed_prefixes: ["app/"],
        source_ref: ".sdlc/gates/paths.yaml",
      },
    ];
    const nodes = buildGateAnnotationNodes(gates, [stageFlowNode("implementation", 50, 80)]);

    expect(nodes).toHaveLength(1);
    expect(nodes[0].id).toBe(gateAnnotationId("implementation"));
    expect(nodes[0].type).toBe("gateAnnotationNode");
  });

  it("strips annotation nodes from export node lists", () => {
    const nodes: CanvasNode[] = [
      {
        id: "display.node.stage.a",
        graph_node_id: "node.stage.a",
        label: "A",
        type: "stage",
        category: "sdlc",
        source_refs: [],
        validation_overlays: [],
      },
      {
        id: agentAnnotationId("qa"),
        graph_node_id: "annotation.agent.qa",
        label: "QA",
        type: "agent_annotation",
        category: "annotation",
        source_refs: [],
        validation_overlays: [],
      },
    ];

    const exportable = annotationNodesForExport(nodes);
    expect(exportable).toHaveLength(1);
    expect(isAnnotationCanvasNode(exportable[0])).toBe(false);
  });
});
