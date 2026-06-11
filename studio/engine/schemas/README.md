# Studio Schemas

This directory contains descriptive YAML schema documents for SDLC Studio Foundation.

The schemas model how Studio may describe existing `.sdlc/`, `.cursor/`, Plane, GitHub, and Studio artifacts. They are contracts for future indexing, visualization, derivation, and validation work, not executable workflow definitions. The Graph IR semantics and source-of-truth boundaries are defined in [`../graph-ir-contract.md`](../graph-ir-contract.md). Validation Result IR semantics are defined in [`../validation-result-ir-contract.md`](../validation-result-ir-contract.md). Compiler/Validator phase boundaries and report semantics are defined in [`../compiler-validator-boundaries.md`](../compiler-validator-boundaries.md).

## Schemas

- `graph.schema.yaml` describes the non-executable Graph IR document shape: graph metadata, nodes, directed edges, annotations, source references, and Validation Result IR attachments. It is a schema document only and does not implement graph compilation, validation, UI mapping, command execution, or workflow execution.
- `workflow.schema.yaml` describes a workflow view built from stages, agents, gates, and transitions. It is descriptive Workflow IR only and does not run stages, enforce gates, invoke agents, or compile workflows.
- `registry-entity.schema.yaml` describes a single referential registry entity.
- `registry-relationship.schema.yaml` describes a single directed referential registry relationship.
- `validation-result.schema.yaml` describes non-executable Validation Result IR records: target references, check categories, outcome status, messages, source references, checker metadata, and timestamps. It does not implement or trigger checks, enforce gates, store durable evidence, or replace Plane/GitHub authority.

## Non-Goals

These schemas do not define compiler execution, validator execution, command behavior, runners, schedulers, LLM orchestration, UI components, API contracts, database models, durable evidence stores, or product runtime behavior.
