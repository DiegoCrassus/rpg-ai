# Skill: Architecture Analysis

## Purpose

Evaluate technical options, define system boundaries, and document architectural decisions before implementation begins.

## When to Use

- At the Architecture stage
- When a new component, integration, or significant change is planned
- When a trade-off decision needs documentation

## Required Inputs

- Approved requirements (from Requirements stage)
- Current architecture state (`docs/architecture/overview.md`, `.sdlc/memory/architecture.md`)
- Existing code structure (inspect `app/`)

## Procedure

1. **Load current architecture** — Read overview, memory, and existing code.
2. **Define technical approach** — How will the requirement be satisfied technically?
3. **Identify boundaries** — What component owns what? What are the interfaces?
4. **Evaluate trade-offs** — List alternatives considered and why the chosen approach was selected.
5. **List impacted areas** — Files, modules, services, docs affected.
6. **Write ADR if needed** — When a significant or non-obvious decision is made.
7. **Identify implementation tasks** — Break the approach into implementable units.

## Outputs

- Technical approach description (1–5 paragraphs)
- Component/boundary diagram or textual description
- Trade-offs table (approach | pros | cons)
- Impacted areas list
- ADR entry (if applicable) in `docs/architecture/decisions.md`
- Implementation task list

## Validation Checklist

- [ ] Trade-offs documented (not just the chosen approach)
- [ ] Impacted areas listed with justification
- [ ] No implementation started before this stage is complete
- [ ] ADR written if a significant decision was made
- [ ] Architecture memory updated if boundaries changed

## Failure Modes

- **Over-engineering** — If the technical approach is more complex than the requirements justify, simplify
- **Missing trade-offs** — Never document only the chosen option; alternatives must be shown
- **Architecture drift** — If the approach contradicts existing decisions, resolve the conflict explicitly
- **Unknown dependencies** — Flag external dependencies as risks if they are not yet confirmed
