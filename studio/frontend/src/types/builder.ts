export type WorkflowTransitionDraft = {
  id: string;
  name: string;
  from_stage: string;
  to_stage: string;
  description: string;
  agent: string;
  skill: string;
  preconditions: string[];
  outputs: string[];
  /** Canvas display edge id — stable key for selection in the builder graph. */
  edgeDisplayId: string;
  sourceDisplayId: string;
  targetDisplayId: string;
};
