export type StudioHealth = {
  status: string;
  service: string;
  version: string;
  repo_root: string;
  repo_root_reachable: boolean;
};

export type SessionGateResponse = {
  present: boolean;
  path: string;
  gate: {
    gate_status?: string;
    card?: string;
    branch?: string;
    stage?: string;
    intent?: string;
  } | null;
};

export type ReadinessMeta = {
  authority?: string;
  overall_status?: string;
  execution_mode?: string;
};

export type ReadinessResponse = {
  readiness?: ReadinessMeta;
  summary?: {
    mvp_ready?: boolean;
    pass?: number;
    warn?: number;
    fail?: number;
  };
};

export type DashboardSummary = {
  authority?: string;
  readiness: {
    overall_status?: string;
    mvp_ready?: boolean;
    pass?: number;
    warn?: number;
    fail?: number;
  };
  session: {
    gate_open?: boolean;
    execution_active?: boolean;
    live_source?: "gate" | "handoff" | "observability" | null;
    inferred_stage?: boolean;
    card?: string;
    branch?: string;
    stage?: string;
    next_agent?: string;
    stage_complete?: string;
  };
  canvas: {
    available?: boolean;
    nodes?: number;
    edges?: number;
    validation_statuses?: Record<string, number>;
  };
  handoff_present?: boolean;
};
