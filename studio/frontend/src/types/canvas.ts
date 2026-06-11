export type ValidationStatus = "pass" | "warn" | "fail" | "not_run";

export type SourceRef = {
  ref_type: string;
  ref: string;
  summary?: string | null;
};

export type ValidationOverlaySummary = {
  id: string;
  status: ValidationStatus;
  check_type: string;
  message_count: number;
  source_refs: SourceRef[];
};

export type CanvasNode = {
  id: string;
  graph_node_id: string;
  label: string;
  type: string;
  category: string;
  source_refs: SourceRef[];
  annotations?: { kind: string; text: string }[];
  validation_overlays: ValidationOverlaySummary[];
};

export type CanvasEdge = {
  id: string;
  graph_edge_id: string;
  source: string;
  target: string;
  relation: string;
  source_refs: SourceRef[];
  validation_overlays: ValidationOverlaySummary[];
  label?: string | null;
  summary?: string | null;
  /** Present on workflow-builder edges from transitions.yaml */
  agent?: string | null;
  skill?: string | null;
};

export type CanvasOverlay = {
  id: string;
  validation_ref: string;
  target: Record<string, string>;
  check_type: string;
  status: ValidationStatus;
  messages: Record<string, unknown>[];
  source_refs: SourceRef[];
};

export type CanvasLegendCategory = {
  id: string;
  label: string;
};

export type CanvasLegend = {
  categories: CanvasLegendCategory[];
  validation_statuses: Record<ValidationStatus, number>;
};

export type CanvasFilters = {
  section: string | null;
  validation_status: ValidationStatus | null;
  entity_type: string | null;
  q: string | null;
};

export type CanvasMeta = {
  total_nodes: number;
  filtered_nodes: number;
  total_edges: number;
  filtered_edges: number;
};

export type CanvasFullResponse = {
  canvas: {
    id: string;
    name?: string;
    authority?: string;
  };
  nodes: CanvasNode[];
  edges: CanvasEdge[];
  overlays: CanvasOverlay[];
  sections: Record<string, unknown>[];
  legend: CanvasLegend;
  filters: CanvasFilters;
  meta: CanvasMeta;
};

export type CanvasNodeDetailResponse = {
  node: CanvasNode;
  overlays: CanvasOverlay[];
};

export type CanvasFilterParams = {
  section?: string;
  validation_status?: ValidationStatus;
  entity_type?: string;
  q?: string;
};
