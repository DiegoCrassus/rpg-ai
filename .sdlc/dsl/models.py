"""Dataclass models for SDLC YAML structures."""

from dataclasses import dataclass, field


@dataclass
class LifecycleStage:
    id: str
    name: str
    order: int
    description: str


@dataclass
class StageDefinition:
    id: str
    name: str
    objective: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    required_evidence: list[str] = field(default_factory=list)
    gates: list[str] = field(default_factory=list)


@dataclass
class Workflow:
    id: str
    name: str
    from_stage: str
    to_stage: str
    description: str
    agent: str | None = None
    skill: str | None = None
    preconditions: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


@dataclass
class Agent:
    id: str
    name: str
    stages: list[str]
    description: str
    primary_skill: str | None = None


@dataclass
class Skill:
    id: str
    name: str
    stages: list[str]
    description: str
    expected_outputs: list[str] = field(default_factory=list)


@dataclass
class Rule:
    id: str
    name: str
    severity: str  # required | warning
    description: str
    enforced_at: list[str] = field(default_factory=list)


@dataclass
class Integration:
    id: str
    name: str
    status: str  # placeholder | not_configured | active
    description: str
    config_env: str | None = None
    capabilities: list[str] = field(default_factory=list)
    notes: str | None = None


@dataclass
class SDLCConfig:
    version: str
    name: str
    description: str
    lifecycle_stages: list[LifecycleStage] = field(default_factory=list)
    stage_definitions: list[StageDefinition] = field(default_factory=list)
    workflows: list[Workflow] = field(default_factory=list)
    agents: list[Agent] = field(default_factory=list)
    skills: list[Skill] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)
    integrations: list[Integration] = field(default_factory=list)
