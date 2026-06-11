export type EvidenceProjection = {
  id: string;
  authority: string;
  template_ref: string;
  execution_mode: string;
  source_refs?: { ref: string }[];
  non_goals?: string[];
  filters?: { card?: string; title?: string; branch?: string };
};

export type EvidenceFields = {
  card: string;
  title: string;
  summary: string;
  problems_solved: string[];
  technical: {
    modules: string[];
    decisions: string[];
    files_changed: string[];
  };
  validation: Record<string, string>;
  artifacts: Record<string, string | string[]>;
  context_for_future: string[];
};

export type EvidenceDraftSummary = {
  template_field_count: number;
  validation_total: number;
  validation_fail: number;
  validation_warn: number;
  validation_pass: number;
  problems_solved_count: number;
  context_for_future_count: number;
};

export type EvidenceDraftResponse = {
  projection: EvidenceProjection;
  summary: EvidenceDraftSummary;
  evidence_fields: EvidenceFields;
};

export type EvidenceDraftParams = {
  card?: string;
  title?: string;
  branch?: string;
};
