import type { CanvasEdge, CanvasNode } from "../../types/canvas";
import type {
  BrokenRefItem,
  RegistryGraphEdge,
  RegistryGraphNode,
  RegistryGraphResponse,
} from "../../types/foundation";

export type BrokenRefIndex = {
  brokenNodeIds: Set<string>;
  brokenEdgeIds: Set<string>;
  panelItems: { id: string; detail: string; kind: "relationship" | "path" }[];
};

export function collectBrokenRefIndex(
  brokenRefs: RegistryGraphResponse["broken_refs"],
  nodes: RegistryGraphNode[],
  edges: RegistryGraphEdge[],
): BrokenRefIndex {
  const brokenNodeIds = new Set<string>();
  const brokenEdgeIds = new Set<string>();
  const panelItems: BrokenRefIndex["panelItems"] = [];

  for (const item of brokenRefs.unresolved_relationships) {
    panelItems.push({ id: item.id, detail: item.detail, kind: "relationship" });
    brokenEdgeIds.add(item.id);
    const edge = edges.find((candidate) => candidate.id === item.id);
    if (edge) {
      brokenNodeIds.add(edge.from);
      brokenNodeIds.add(edge.to);
    }
  }

  for (const item of brokenRefs.missing_optional_source_paths) {
    panelItems.push({ id: item.id, detail: item.detail, kind: "path" });
    for (const node of nodes) {
      const matchesPath = node.source_refs.some((ref) => ref.ref === item.id);
      if (matchesPath) {
        brokenNodeIds.add(node.id);
      }
    }
  }

  return { brokenNodeIds, brokenEdgeIds, panelItems };
}

function toCanvasNode(node: RegistryGraphNode, brokenNodeIds: Set<string>): CanvasNode {
  const isBroken = brokenNodeIds.has(node.id);
  return {
    id: node.id,
    graph_node_id: node.id,
    label: node.label,
    type: node.type,
    category: node.category,
    source_refs: node.source_refs,
    annotations: node.annotations,
    validation_overlays: isBroken
      ? [
          {
            id: `broken.${node.id}`,
            status: "fail",
            check_type: "registry",
            message_count: 1,
            source_refs: node.source_refs,
          },
        ]
      : [],
  };
}

function toCanvasEdge(edge: RegistryGraphEdge, brokenEdgeIds: Set<string>): CanvasEdge {
  const isBroken = brokenEdgeIds.has(edge.id);
  return {
    id: edge.id,
    graph_edge_id: edge.id,
    source: edge.from,
    target: edge.to,
    relation: edge.relation,
    source_refs: edge.source_refs,
    label: edge.summary,
    validation_overlays: isBroken
      ? [
          {
            id: `broken.${edge.id}`,
            status: "fail",
            check_type: "registry",
            message_count: 1,
            source_refs: edge.source_refs,
          },
        ]
      : [],
  };
}

export function mapRegistryGraphToCanvas(
  response: RegistryGraphResponse,
): { nodes: CanvasNode[]; edges: CanvasEdge[]; broken: BrokenRefIndex } {
  const broken = collectBrokenRefIndex(response.broken_refs, response.nodes, response.edges);
  return {
    nodes: response.nodes.map((node) => toCanvasNode(node, broken.brokenNodeIds)),
    edges: response.edges.map((edge) => toCanvasEdge(edge, broken.brokenEdgeIds)),
    broken,
  };
}

export function scenarioSlugFromId(scenarioId: string): string {
  const prefix = "simulation.scenario.";
  return scenarioId.startsWith(prefix) ? scenarioId.slice(prefix.length) : scenarioId;
}

export function pathLabelChipClass(label: string): string {
  switch (label) {
    case "expected":
      return "border-emerald-500/50 bg-emerald-500/10 text-emerald-200";
    case "blocked":
      return "border-studio-fail/50 bg-red-950/40 text-red-200";
    case "unsupported":
      return "border-amber-500/40 bg-amber-500/10 text-amber-200";
    default:
      return "border-slate-600 bg-slate-800/60 text-slate-300";
  }
}

export function doctorChipClass(exitCode: number | null | undefined): string {
  if (exitCode === 0) {
    return "border-emerald-500/50 bg-emerald-500/10 text-emerald-200";
  }
  if (exitCode === 1) {
    return "border-studio-fail/50 bg-red-950/40 text-red-200";
  }
  return "border-slate-600 bg-slate-800/60 text-slate-400";
}

export function brokenRefItems(brokenRefs: RegistryGraphResponse["broken_refs"]): BrokenRefItem[] {
  return [
    ...brokenRefs.unresolved_relationships,
    ...brokenRefs.missing_optional_source_paths,
  ];
}
