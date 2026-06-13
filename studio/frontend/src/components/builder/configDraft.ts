import type { ConfigKind } from "../../types/config";
import type { ProposalCreateRequest, ProposalKind } from "../../types/proposals";
import { DEFAULT_PLANE_CARD } from "../../constants/plane";

const SLUG_RE = /^[a-z][a-z0-9-]*$/;

export type ConfigBuilderMode = "edit" | "create";

export type ConfigKindMeta = {
  kind: ConfigKind;
  label: string;
  pathHint: string;
  defaultTitle: string;
  gateStage: "sdlc_meta";
};

export const CONFIG_KIND_META: Record<ConfigKind, ConfigKindMeta> = {
  agent: {
    kind: "agent",
    label: "Agent",
    pathHint: ".cursor/agents/<slug>.md",
    defaultTitle: "New or updated agent",
    gateStage: "sdlc_meta",
  },
  rule: {
    kind: "rule",
    label: "Rule",
    pathHint: ".cursor/rules/<slug>.mdc",
    defaultTitle: "New or updated rule",
    gateStage: "sdlc_meta",
  },
  skill: {
    kind: "skill",
    label: "Skill",
    pathHint: ".cursor/skills/<slug>/SKILL.md",
    defaultTitle: "New or updated skill",
    gateStage: "sdlc_meta",
  },
  command: {
    kind: "command",
    label: "Command",
    pathHint: ".cursor/commands/<slug>.md",
    defaultTitle: "New or updated command",
    gateStage: "sdlc_meta",
  },
};

export function normalizeSlug(raw: string): string {
  return raw
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function isValidSlug(slug: string): boolean {
  return SLUG_RE.test(slug);
}

export function targetPathForSlug(kind: ConfigKind, slug: string): string {
  switch (kind) {
    case "agent":
      return `.cursor/agents/${slug}.md`;
    case "rule":
      return `.cursor/rules/${slug}.mdc`;
    case "skill":
      return `.cursor/skills/${slug}/SKILL.md`;
    case "command":
      return `.cursor/commands/${slug}.md`;
    default:
      return `.cursor/${slug}`;
  }
}

export function templateContent(kind: ConfigKind, slug: string, description: string): string {
  const desc = description.trim() || `Studio draft ${kind} ${slug}`;
  switch (kind) {
    case "agent":
      return `---
name: ${slug}
description: "${desc.replace(/"/g, '\\"')}"
model: inherit
readonly: false
---

# Subagent: ${slug}

## Role

Describe the agent role.

## Responsibilities

- 

## Boundaries

- Does not merge PRs or skip SDLC gates.
`;
    case "rule":
      return `---
description: ${desc}
alwaysApply: false
---

# ${slug}

Describe when this rule applies.
`;
    case "skill":
      return `# Skill: ${slug}

## Purpose

${desc}

## When to use

- 

## Procedure

1. 
`;
    case "command":
      return `# Command: ${slug}

## Purpose

${desc}

## When to Use

- 

## Procedure

1. 
`;
    default:
      return `# ${slug}\n\n${desc}\n`;
  }
}

export function buildConfigProposalRequest(options: {
  kind: ConfigKind;
  path: string;
  content: string;
  title: string;
  card: string;
  mode: ConfigBuilderMode;
  exists: boolean;
}): ProposalCreateRequest {
  const meta = CONFIG_KIND_META[options.kind];
  const op =
    options.mode === "create" || !options.exists
      ? ("create_file" as const)
      : ("replace_block" as const);

  return {
    kind: options.kind as ProposalKind,
    title: options.title.trim() || meta.defaultTitle,
    target_paths: [options.path],
    ops: [
      {
        op,
        path: options.path,
        content: options.content,
      },
    ],
    simulated_gate: {
      stage: meta.gateStage,
      card: options.card.trim() || DEFAULT_PLANE_CARD,
    },
  };
}
