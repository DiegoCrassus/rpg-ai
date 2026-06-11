# Business Rules

Numbered rules derived from the initial brief, refined for implementation.

## Users and Mesas

| ID | Rule |
|----|------|
| BR-01 | Any authenticated user may create up to **2 Mesas as Master**. |
| BR-02 | Mesa creator is the **sole Master** — exactly one Master per Mesa. |
| BR-02a | New Mesa starts in `importing` status until sheet template is approved or seed fallback applied. |
| BR-03 | A user may participate in multiple Mesas simultaneously. |
| BR-04 | A user may be Master in one Mesa and Player in another. |
| BR-05 | A Player may join a Mesa only via a valid invite (single-use token, not expired). |
| BR-05a | A user may be Master in at most 2 Mesas and Player in unlimited other Mesas. |
| BR-06 | Each Mesa owns its documents, sheet templates, and character sheets; no cross-Mesa references. |

## Roles and access

| ID | Rule |
|----|------|
| BR-07 | Master has full read/write access to all data within their Mesa. |
| BR-08 | Player sees only documents and sheets explicitly permitted. |
| BR-09 | Admin has global access for platform operations and audit. |
| BR-10 | Every permission check MUST include Mesa context (membership + role). |
| BR-11 | Removing a Player revokes access immediately; their content may be retained or archived per Mesa policy. |

## Invites

| ID | Rule |
|----|------|
| BR-12 | Only Admin or Mesa Master may create or revoke invites. |
| BR-13 | Invites expire **7 days** after creation; expired invites cannot be accepted. |
| BR-14 | Accepting an invite consumes the token (`used_at` set); token cannot be reused. |
| BR-15 | Accepting user must be authenticated; **invite email must match** account email (Q-015). |

## Character sheets

| ID | Rule |
|----|------|
| BR-16 | Sheet templates are defined per Mesa; multiple active templates allowed. |
| BR-16a | Default Mesa bootstrap: Master uploads PDF/PNG → Sheet Import Agent proposes template; Master must approve before Mesa becomes `active`. |
| BR-16b | Platform D&D 5e seed is fallback when import is skipped, rejected, or low confidence. |
| BR-17 | A character sheet belongs to exactly one Mesa and one owning Player. |
| BR-18 | Master may view and edit all character sheets in the Mesa. |
| BR-19 | Player may edit own sheet only if Mesa settings allow. |
| BR-20 | Player may view another player's sheet only if Master grants it. |

## Documents and visibility

| ID | Rule |
|----|------|
| BR-21 | Documents may have visibility scoped to Master, all Players, specific Players, or a character. |
| BR-22 | Master always bypasses document visibility restrictions within their Mesa. |
| BR-23 | Document type is metadata for organization and filtering; it does not change permission logic. |
| BR-24 | Document delete is **soft-delete** (`deleted_at`); hard purge Admin-only (Q-016). |

## Audit and history

| ID | Rule |
|----|------|
| BR-25 | Significant changes (sheet edits, document edits, role changes) SHOULD be logged. |
| BR-26 | Version history for sheets, templates, and documents — snapshot on save in MVP. |
| BR-29 | All content payloads (sheet JSON, documents, media) live in Supabase Storage under `campaigns/{mesa_id}/`; Postgres holds metadata and `storage_path` pointers. |
| BR-31 | API mediates all Storage access — clients do not write to `campaigns` bucket directly in MVP. |
| BR-30 | Authentication via Supabase Auth (email + OAuth); **Google OAuth required** in MVP; backend validates JWT. |
| BR-32 | UI copy and labels in **PT-BR** for MVP (Q-012). |
| BR-33 | Document and character story body format: **Markdown** default (Q-014). |
| BR-34 | Computed sheet field types are **not supported** in MVP (Q-005). |

## Platform

| ID | Rule |
|----|------|
| BR-27 | Suspended users cannot access any Mesa. |
| BR-28 | Archived Mesas are read-only for Players; Masters may restore to `active`. |
