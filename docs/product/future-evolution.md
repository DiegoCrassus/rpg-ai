# Future Evolution

Post-MVP capabilities in suggested order. Not committed — sequencing may change after MVP feedback.

## Phase 2 — Depth

| Feature | Value |
|---------|-------|
| **Mesa templates** | Pre-built sheet + document sets (D&D 5e, Tormenta20, Vampiro, etc.) |
| **Version history UI** | Restore previous sheet/document versions |
| **File uploads** | Images, PDFs attached to documents and sheets |
| **Sessions module** | Structured session entity linked to NPCs, locations, characters |
| **Entity relationships** | NPC ↔ faction, item ↔ character, session ↔ revelation |
| **Timeline** | Campaign chronology with visibility control |
| **OAuth login** | Google / Discord |

## Phase 3 — Narrative power

| Feature | Value |
|---------|-------|
| **Layered secrets** | Public / character / Master layers on one document |
| **Revelation mechanics** | Master unlocks information progressively per player |
| **Personal timelines** | Per-character story arc view |
| **Resource library** | Reusable NPCs, items, locations across Mesas (user-owned) |

## Phase 4 — Ecosystem

| Feature | Value |
|---------|-------|
| **Template marketplace** | Community-shared Mesa and sheet templates |
| **Discord bot** | Notifications, slash commands for sheet lookup |
| **API for third parties** | Read-only public campaign wikis |
| **Mobile app** | Native or PWA optimized |

## Phase 5 — AI assistant (optional)

| Capability | Guardrail |
|------------|-----------|
| Session summarization | Master approves before Players see |
| NPC / location generation | Master edits before publish |
| Lore inconsistency detection | Suggestions only; no auto-edits |
| Note → structured document | Opt-in per Mesa |

AI features require explicit Mesa-level opt-in and must respect visibility rules.

## Technical debt to plan early

| Item | Why early |
|------|-----------|
| Mesa-scoped query middleware | Hard to retrofit |
| JSON schema validation for sheets | Prevents template corruption |
| Audit log table | Needed before Admin grows |
| Soft-delete pattern | Safer document/sheet removal |
| i18n keys in frontend | Adopt in v1.1 (Q-012: PT-BR only in MVP) |
