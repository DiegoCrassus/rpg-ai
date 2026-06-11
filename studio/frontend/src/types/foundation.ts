import type { SourceRef } from "./canvas";

export type BrokenRefItem = {
  id: string;
  detail: string;
};

export type RegistryGraphNode = {
  id: string;
  type: string;
  category: string;
  label: string;
  registry_ref?: string | null;
  entity_ref?: string | null;
  source_refs: SourceRef[];
  annotations?: { kind: string; text: string }[];
};

export type RegistryGraphEdge = {
  id: string;
  from: string;
  to: string;
  relation: string;
  source_refs: SourceRef[];
  summary?: string | null;
};

export type RegistryGraphResponse = {
  graph: {
    id: string;
    name?: string;
    authority?: string;
  };
  nodes: RegistryGraphNode[];
  edges: RegistryGraphEdge[];
  broken_refs: {
    unresolved_relationships: BrokenRefItem[];
    missing_optional_source_paths: BrokenRefItem[];
  };
  summary: {
    status?: string;
    broken_ref_count: number;
    counts?: Record<string, number>;
  };
};

export type ValidationRecord = {
  id: string;
  validation_ref: string;
  status: "pass" | "warn" | "fail" | "not_run";
  check_type: string;
  target: { ref_type: string; ref: string };
  messages: { level?: string; text?: string }[];
  source_refs: SourceRef[];
  summary: string;
};

export type ValidationInspectResponse = {
  inspection: {
    id: string;
    authority?: string;
    group_by?: string;
  };
  groups: {
    id: string;
    key: string;
    label: string;
    count: number;
  }[];
  records: ValidationRecord[];
  summary: {
    total_records: number;
    visible_records: number;
    by_status?: Record<string, number>;
  };
};

export type DoctorRunResponse = {
  exit_code: number;
  summary: string;
  details: { label?: string; value?: string }[];
};

export type SimulationStep = {
  id: string;
  order: number;
  kind: string;
  ref: string;
  path_label: "expected" | "blocked" | "unsupported" | string;
  summary: string;
  lifecycle_source?: string | null;
  source_refs?: SourceRef[];
  next_agent_recommendation?: string | null;
  exit_criteria?: string | null;
};

export type SimulationScenario = {
  id: string;
  name: string;
  intent: string;
  description: string;
  tags?: string[];
  outcome?: string;
  steps: SimulationStep[];
};

export type SimulationPreviewResponse = {
  simulation: {
    id: string;
    authority?: string;
    execution_mode?: string;
    filters?: { scenario?: string | null };
  };
  summary: {
    scenario_count: number;
    step_count: number;
    path_labels?: Record<string, number>;
  };
  scenarios: SimulationScenario[];
};

export type AssistanceSuggestion = {
  id: string;
  kind: string;
  status: string;
  summary: string;
  observed?: string;
  proposed?: string;
  source_refs: SourceRef[];
};

export type WorkflowAssistanceResponse = {
  assistance: {
    id: string;
    authority?: string;
  };
  summary: Record<string, unknown>;
  suggestions: AssistanceSuggestion[];
  explanations?: { id: string; summary: string }[];
};

export type ValidationInspectParams = {
  status?: string;
  check_type?: string;
  target_type?: string;
  group_by?: string;
};

export type SimulationPreviewParams = {
  scenario?: string;
};

export type WorkflowAssistanceParams = {
  kind?: string;
};
