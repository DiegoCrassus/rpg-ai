# Publish Evidence Workflow Prototype

Deterministic evidence-field projection for `INVES-72` (roadmap phase 9). Maps derived Studio pipeline outputs to the Plane evidence template field shape without posting, executing gates, or writing JSON files. Template: `.sdlc/templates/plane/evidence-template.json`. Roadmap: `docs/roadmap/sdlc-studio-mvp-roadmap.md`.

Pipeline: compile → validate → canvas → validation_inspection → publish_evidence.

CLI:

```bash
python -m studio.cli publish-evidence [--format text|json] [--root PATH] \
  [--card INVES-N] [--title TITLE] [--branch BRANCH]
```

Output: `projection` (`derived_non_authoritative`, `execution_mode=non_executing_projection`), `summary`, and `evidence_fields` matching the template top-level keys (`card`, `title`, `summary`, `problems_solved`, `technical`, `validation`, `artifacts`, `context_for_future`). All metadata cites `source_refs` only.

Non-goals: no Plane/GitHub mutation, no pytest/doctor/CI execution, no persistence, no authoritative QA or gate claims. Implementation: `studio/publish_evidence.py`.

## Rollback and roll-forward (AC-4)

Studio metadata changes (schemas, registry YAML, CLI flags, prototype docs) ship via normal feature branches and PRs to `develop`.

- **Rollback:** revert the offending commit or open a revert PR on the same paths (`.sdlc/registry/`, `.sdlc/templates/`, `studio/*.py`, `studio/ai-*.md`). Regenerated projections pick up the prior sources on the next CLI run; no migration or runtime state to unwind.
- **Roll-forward:** prefer a follow-up Plane child card when the evidence template, registry entries, or projection fields need additive fixes. Keep source edits separate from any generated CLI output in the PR diff.
- **`context_for_future`:** operators should cite the rollback path (revert PR) or roll-forward card ID when posting evidence to Plane so reviewers can trace metadata lineage.
