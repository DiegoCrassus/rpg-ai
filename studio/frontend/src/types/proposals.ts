export type ProposalKind = "workflow" | "agent" | "rule" | "skill" | "command";
export type ProposalOp = "replace_block" | "insert_after" | "delete_lines" | "create_file";
export type GateStage = "planning" | "architecture" | "sdlc_meta";
export type DryRunStep = "validate" | "doctor" | "gateway-check";

export type StructuredOp = {
  op: ProposalOp;
  path: string;
  anchor?: string | null;
  content?: string | null;
};

export type SimulatedGate = {
  stage: GateStage;
  card: string;
};

export type ProposalCreateRequest = {
  kind: ProposalKind;
  title: string;
  target_paths: string[];
  ops: StructuredOp[];
  simulated_gate: SimulatedGate;
};

export type DryRunResult = {
  proposal_id: string;
  step: DryRunStep;
  exit_code: 0 | 1;
  summary: string;
  details: Record<string, unknown>[];
};

export type ProposalResponse = {
  proposal_id: string;
  kind: ProposalKind;
  title: string;
  target_paths: string[];
  patch_format: "unified_diff";
  patch_body: string;
  authority_badge: "proposed_non_authoritative";
  simulated_gate: SimulatedGate;
  created_at: string;
  dry_runs: Partial<Record<DryRunStep, DryRunResult>>;
};
