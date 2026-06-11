# Skill: Requirements Refinement

## Purpose

Convert a raw idea, ticket, or request into a structured specification that can drive architecture and implementation.

## When to Use

- At the Ticket or Requirements stage
- When a request lacks acceptance criteria or scope boundaries
- When risks or non-goals are not explicit

## Required Inputs

- Raw request or ticket description
- Business context (from `.sdlc/memory/business-rules.md`)
- Current system boundaries (from `.sdlc/memory/architecture.md`)

## Procedure

1. **Read context** — Load business rules and architecture memory.
2. **Extract intent** — What is the user/business trying to achieve?
3. **Define scope** — What is explicitly in scope?
4. **Define non-goals** — What is explicitly out of scope?
5. **Write acceptance criteria** — Minimum 3, each measurable.
6. **Identify assumptions** — Anything not stated but inferred.
7. **Identify risks** — Minimum 2, with likelihood and impact.
8. **List constraints** — Technical, business, or compliance constraints.

## Outputs

- Scope statement (1–3 sentences)
- Non-goals list (at least 2)
- Acceptance criteria (at least 3, measurable)
- Assumptions list with confidence level (high/medium/low)
- Risk registry (at least 2 entries)
- Constraints list

## Validation Checklist

- [ ] Each acceptance criterion can be verified without ambiguity
- [ ] Non-goals prevent scope creep
- [ ] Risks have mitigations or accepted status
- [ ] Assumptions are explicit, not hidden
- [ ] No undefined business terms used without explanation

## Failure Modes

- **Vague acceptance criteria** — Ask for examples; never accept "it should work correctly"
- **Missing non-goals** — Ask "what are you NOT trying to do?"
- **No risks identified** — Prompt with: performance, security, data loss, user impact
- **Unknown domain terms** — Ask for definition; do not invent meaning
