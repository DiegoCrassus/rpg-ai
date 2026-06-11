export type PipelineStageMeta = {
  id: string;
  name: string;
  order?: number;
  description: string;
};

export type PipelineAgentMeta = {
  id: string;
  name: string;
  stages: string[];
  cursor_agent: string;
  skill: { id: string; name: string };
};

export type PipelineSkillMeta = {
  id: string;
  name: string;
};

export type PipelineGateMeta = {
  id: string;
  name: string;
  stage: string;
  allowed_prefixes: string[];
  source_ref: string;
};

export type PipelineMetadataResponse = {
  stages: PipelineStageMeta[];
  agents: PipelineAgentMeta[];
  skills: PipelineSkillMeta[];
  gates: PipelineGateMeta[];
  summary: {
    stage_count: number;
    agent_count: number;
    skill_count: number;
    gate_count: number;
    transition_count: number;
  };
  source_refs: string[];
};
