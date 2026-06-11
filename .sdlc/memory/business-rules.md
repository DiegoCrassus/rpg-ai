# Business Rules Memory

> Core business rules and domain constraints. Update when rules change or are discovered.

## Current State

**Status:** Initialization — product features not yet defined.

## Known Rules

- This repository is the SDLC operating system itself, not a product.
- The SDLC model follows 10 stages: ticket → requirements → architecture → implementation → validation → review → deployment → observability → incident → autofix.
- All work must pass Doctor validation after structural changes.
- Documentation must be kept in sync with code changes.

## Domain Invariants

_To be defined as the product is built._

## Acceptance Criteria Conventions

- Criteria must be measurable and explicit.
- "It works" is not an acceptance criterion.
- Each ticket must have at least 3 criteria.

## Non-Negotiables

- No fake validation results.
- No broad rewrites without documented reason.
- Human review required before auto-fix merges.
