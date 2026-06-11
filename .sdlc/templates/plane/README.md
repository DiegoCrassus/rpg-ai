# Plane evidence templates

> **Parent:** [`../README.md`](../README.md) · **Scripts:** `.sdlc/scripts/plane_evidence.py`, `.sdlc/scripts/plane_card.py`

## Purpose

Examples and payload shapes for structured Plane evidence comments.

## Existing files

| File | Meaning |
|------|---------|
| `evidence-template.json` | Canonical evidence payload shape for Plane comments |

## When to use

Use this file as the starting shape when a DevOps or Reviewer step needs a structured evidence payload. Fill it with real evidence for the active card before posting.

## Do not

- Treat this template as active evidence without filling it for the current card.
- Store local task plans here.
- Commit credentials, tokens, or raw private API responses.
