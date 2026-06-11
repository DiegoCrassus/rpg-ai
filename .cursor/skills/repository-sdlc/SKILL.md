---
name: repository-sdlc
description: Work with repository pull requests, CI status, issue links, releases, and merge evidence for the SDLC pipeline. Use when DevOps, Reviewer, or Orchestrator needs repository context, PR creation, CI checks, or merge status.
disable-model-invocation: true
---

# Repository SDLC

## Purpose

Standardize repository operations in the SDLC pipeline. The **board** remains the primary workboard; the **repository** (provider: GitHub) is used for PRs, CI evidence, issue triage, and merge records.

## When to use

- Creating or reviewing a PR for an `RPG-N` card.
- Checking CI before `workflow finish`.
- Linking repository issues to board cards.
- Preparing release or rollback notes tied to a PR.

## Procedure

1. Read `.sdlc/process/change-lifecycle.md`.
2. Confirm the active board card and branch from `.sdlc/memory/orchestrator-handoff.md` and `workflow status`.
3. Use the repository default base branch from `.sdlc/sdlc.yaml` (`develop`).
4. Collect real evidence: PR URL, CI status, merge commit, rollback command.
5. Record evidence on the board through `finish-change` / DevOps flow.

## Boundaries

- Do not use repository issues as the primary tracker; board cards are source of truth.
- Do not merge without Reviewer APPROVE and green CI.
- Do not force-push or bypass branch protections.

## Related files

- `.cursor/skills/finish-change/SKILL.md`
- `.sdlc/scripts/auto_merge_pr.py`
- `.sdlc/scripts/github_issue_triage.py`
- `.sdlc/integrations/services.yaml`
