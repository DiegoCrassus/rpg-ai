#!/usr/bin/env python3
"""Create RPG Platform MVP epic + three child cards on Plane (idempotent check)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import httpx

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from board_client import board_api, format_card  # noqa: E402
from plane_html import build_plan_html, bullet_list, document, heading, paragraph_text  # noqa: E402

EPIC_TITLE = "[AI][EPIC] RPG Platform MVP"


def _headers(api_key: str) -> dict[str, str]:
    return {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _issues_url(workspace: str, project_id: str) -> str:
    return (
        f"https://api.plane.so/api/v1/workspaces/{workspace}/"
        f"projects/{project_id}/issues/"
    )


def resolve_state_id(
    api_key: str, workspace: str, project_id: str, *, name: str = "Todo"
) -> str:
    url = (
        f"https://api.plane.so/api/v1/workspaces/{workspace}/"
        f"projects/{project_id}/states/"
    )
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=_headers(api_key))
        resp.raise_for_status()
        data = resp.json()
        items = data if isinstance(data, list) else data.get("results") or []
        for item in items:
            if (item.get("name") or "").strip().lower() == name.lower():
                return str(item["id"])
    sys.exit(f"ERROR: Plane state '{name}' not found in project {project_id}")


def list_issues(api_key: str, workspace: str, project_id: str) -> list[dict]:
    url = _issues_url(workspace, project_id)
    items: list[dict] = []
    cursor = ""
    with httpx.Client(timeout=60.0) as client:
        while True:
            params: dict[str, str | int] = {"per_page": 100}
            if cursor:
                params["cursor"] = cursor
            resp = client.get(url, headers=_headers(api_key), params=params)
            if resp.status_code == 403:
                sys.exit(
                    "ERROR: Plane API 403 — PLANE_API_KEY invalid or lacks project access. "
                    "Regenerate at Profile Settings → Personal Access Tokens, update .env, "
                    "then re-run: python .sdlc/scripts/plane_create_mvp_epic.py"
                )
            resp.raise_for_status()
            data = resp.json()
            items.extend(data.get("results") or [])
            cursor = data.get("next_cursor") or ""
            if not cursor or not data.get("next_page_results"):
                break
    return items


def create_issue(
    api_key: str,
    workspace: str,
    project_id: str,
    *,
    name: str,
    description_html: str,
    parent: str | None = None,
    todo_state_id: str,
) -> dict:
    payload: dict[str, str] = {
        "name": name,
        "description_html": description_html,
        "state": todo_state_id,
    }
    if parent:
        payload["parent"] = parent
    url = _issues_url(workspace, project_id)
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, headers=_headers(api_key), json=payload)
        if resp.status_code >= 400:
            sys.exit(f"ERROR: create issue failed ({resp.status_code}): {resp.text[:500]}")
        return resp.json()


def patch_description(
    api_key: str, workspace: str, project_id: str, issue_uuid: str, html: str
) -> None:
    url = f"{_issues_url(workspace, project_id)}{issue_uuid}/"
    with httpx.Client(timeout=60.0) as client:
        resp = client.patch(url, headers=_headers(api_key), json={"description_html": html})
        resp.raise_for_status()


def epic_html(infra_id: str, backend_id: str, frontend_id: str) -> str:
    base = build_plan_html(
        {
            "task_name": EPIC_TITLE,
            "story": [
                "The repository has complete product specs and approved architecture "
                "(ADR-011 through ADR-015) but no application code under app/. "
                "Investment Radar is superseded; RPG Platform is the new product focus.",
                "MVP must validate organization and access control for tabletop RPG "
                "campaigns (Mesas): Mesa isolation, role-aware permissions, sheet "
                "import bootstrap, documents, and character sheets before gameplay tooling.",
                "This epic delivers the full greenfield stack: Supabase local infra, "
                "FastAPI backend with Sheet Import Deep Agent, and React PT-BR frontend.",
            ],
            "scope": [
                "Three child cards: INFRA → BACKEND → FRONTEND (sequential workflow start)",
                "Supabase Auth + PostgreSQL + Storage local dev stack",
                "FastAPI /api/v1/ with Mesa lifecycle, import agent, documents, sheets",
                "React SPA with auth, Mesa bootstrap, sheet renderer, wiki/documents",
                "Shared JSON Schema contracts and D&D 5e seed in app/shared/",
                "OpenAPI, Makefile targets, .env.example for local bootstrap",
            ],
            "non_goals": [
                "Dice rolling, combat automation, tactical maps (never MVP)",
                "Real-time chat, AI assistant, template marketplace (v2+)",
                "Self-hosted auth without Supabase; direct client Storage writes",
                "Entity graph, timeline, layered secret revelations (v2)",
            ],
            "assumptions": [
                ["Supabase CLI + Docker available on dev machines", "high", "Block INFRA child"],
                ["OpenAI API key available for Sheet Import Agent", "high", "Import flow stubbed or blocked"],
                ["Product docs in docs/product/ frozen for MVP", "high", "Scope churn mid-implementation"],
                ["Authorization in FastAPI policy layer; RLS deferred", "medium", "Architect must confirm"],
                ["Single Master per Mesa; max 2 Mesas as Master per user", "high", "Business rule violation"],
            ],
            "risks": [
                [
                    "Deep Agent sheet import quality varies by PDF/scan",
                    "medium",
                    "high",
                    "Master review UI + D&D 5e seed fallback path",
                ],
                [
                    "Three-layer greenfield with empty app/ — integration gaps",
                    "medium",
                    "high",
                    "Strict child order INFRA→BACKEND→FRONTEND; OpenAPI contract gate",
                ],
                [
                    "Supabase local stack drift vs cloud",
                    "low",
                    "medium",
                    "Document env vars; pin supabase CLI version in Makefile",
                ],
            ],
            "impacted_areas": [
                "app/infra/ ← new (Supabase config, compose)",
                "app/shared/ ← new (JSON Schema, dnd5e seed)",
                "app/backend/ ← new (FastAPI modules per docs/product/modules.md)",
                "app/frontend/ ← new (React SPA PT-BR)",
                ".env.example ← update",
                "Makefile ← update (supabase, dev targets)",
                "docs/product/* ← reference only (no scope change)",
            ],
            "acceptance_criteria": [
                "AC-1: All three child cards exist on Plane with parent = this epic",
                "AC-2: validate-all passes on epic (plan + granularity ≥3 children)",
                "AC-3: Each child has ≥3 acceptance criteria and branch slug hint",
                "AC-4: Epic Done only when INFRA, BACKEND, FRONTEND children are Done",
                "AC-5: MVP user journeys 1–3 in docs/product/mvp-scope.md achievable end-to-end",
            ],
            "definition_of_done": [
                "All child cards merged to develop with green CI",
                "make sdlc-doctor exits 0",
                "Local dev documented: supabase start + backend + frontend",
                "No secrets committed; .env.example complete",
                "Epic evidence posted on Plane when all children Done",
            ],
            "next_step": (
                "Architect: confirm module boundaries, auth bridge, Storage orchestration, "
                "and Deep Agent workspace contract before workflow start on INFRA child."
            ),
        }
    )
    breakdown = document(
        heading("Task Breakdown"),
        bullet_list(
            [
                f"{infra_id}: [AI][INFRA] Supabase local, shared contracts, env bootstrap "
                "— branch feature/{id}-infra-supabase-contracts",
                f"{backend_id}: [AI][BACKEND] API, auth bridge, mesas, import agent, "
                "documents, sheets — branch feature/{id}-backend-api-mesas-agent",
                f"{frontend_id}: [AI][FRONTEND] Auth, Mesa bootstrap, sheet renderer, wiki "
                "— branch feature/{id}-frontend-auth-mesa-sheets",
            ]
        ),
    )
    return base.replace("</div>", breakdown.replace("<div>", "") + "</div>", 1)


def infra_html() -> str:
    return build_plan_html(
        {
            "task_name": "[AI][INFRA] Supabase local, shared contracts, env bootstrap",
            "story": [
                "Greenfield RPG Platform has zero app/ code. Backend and frontend need a "
                "shared local Supabase stack and canonical JSON contracts before implementation.",
                "This child establishes Supabase CLI local dev, app/infra/ configuration, "
                "app/shared/ JSON Schema envelopes + D&D 5e seed, and Makefile/SDLC targets "
                "so downstream cards can start against a reproducible environment.",
            ],
            "scope": [
                "Supabase CLI local dev (supabase start): Auth, PostgreSQL, Storage",
                "app/infra/ — supabase config, migrations scaffold, docker/compose if needed",
                "app/shared/ — JSON Schema contracts per docs/product/json-contracts.md",
                "D&D 5e sheet seed as import fallback per docs/product/dnd5e-sheet-reference.md",
                "Storage bucket layout aligned with docs/product/storage-layout.md",
                ".env.example with SUPABASE_*, DATABASE_URL, AGENT_MODEL placeholders",
                "Makefile targets: supabase-up, supabase-down, dev bootstrap hints",
            ],
            "non_goals": [
                "Production cloud Supabase provisioning (future ops card)",
                "Backend API routes or frontend UI",
                "Sheet Import Agent runtime (BACKEND child)",
            ],
            "assumptions": [
                ["Docker available for supabase start", "high", "Local dev blocked"],
                ["Postgres schema matches docs/product/database-schema.md at high level", "medium", "Architect gate"],
                ["Single-region; no multi-tenant infra", "high", "Over-engineering if wrong"],
            ],
            "risks": [
                [
                    "Supabase CLI version mismatch across dev machines",
                    "medium",
                    "medium",
                    "Pin CLI version in docs/Makefile; document minimum version",
                ],
                [
                    "JSON Schema drift from product contracts",
                    "medium",
                    "high",
                    "Validate schemas against docs/product/json-contracts.md in CI stub",
                ],
            ],
            "impacted_areas": [
                "app/infra/ ← new",
                "app/shared/schemas/ ← new",
                "app/shared/seeds/dnd5e/ ← new",
                "supabase/ ← new (migrations, config.toml)",
                ".env.example ← update",
                "Makefile ← update",
            ],
            "acceptance_criteria": [
                "AC-1: supabase start succeeds; Auth, Postgres, Storage reachable on localhost",
                "AC-2: app/shared/ contains versioned JSON Schema for sheet template + character envelopes",
                "AC-3: D&D 5e seed JSON present and validates against schema",
                "AC-4: .env.example documents all required vars per docs/product/infrastructure.md",
                "AC-5: make target (or documented command) boots local Supabase stack",
            ],
            "definition_of_done": [
                "Local Supabase stack starts cleanly from documented steps",
                "Shared contracts validate (schema lint or pytest stub)",
                "make sdlc-doctor exits 0",
                "PR merged to develop; evidence on Plane card",
                "No secrets in repo",
            ],
            "next_step": "Unblocks BACKEND child — hand off schema paths and env contract.",
        }
    )


def backend_html() -> str:
    return build_plan_html(
        {
            "task_name": "[AI][BACKEND] API, auth bridge, mesas, import agent, documents, sheets",
            "story": [
                "With INFRA providing Supabase local stack and shared contracts, the backend "
                "implements the FastAPI application layer: JWT validation, authorization policy, "
                "Mesa lifecycle, and Storage orchestration.",
                "MVP requires Mesas starting in importing status, Sheet Import Deep Agent "
                "proposal flow, documents with visibility rules, character sheets with version "
                "snapshots, invites, and minimal admin — all under /api/v1/.",
            ],
            "scope": [
                "FastAPI app at app/backend/ with /api/v1/ prefix and OpenAPI",
                "Supabase JWT validation (JWKS) + FastAPI policy layer",
                "Users/profiles sync; avatar via Storage",
                "Mesas CRUD + status lifecycle importing → active",
                "Sheet Import Deep Agent runner (LangChain deepagents, gpt-4.1-mini)",
                "Import upload, job status, master approve/reject/fallback",
                "Participants, invites (7-day single-use tokens)",
                "Documents CRUD + visibility (master_only, all_players, specific_players)",
                "Sheet templates + character sheets + Storage integration + version snapshots",
                "Minimal admin: list users/mesas, suspend user",
            ],
            "non_goals": [
                "Frontend UI (FRONTEND child)",
                "RLS policies in Postgres (deferred per ADR-011)",
                "Direct client Storage writes",
            ],
            "assumptions": [
                ["INFRA child merged; local Supabase + schemas available", "high", "Blocked until INFRA Done"],
                ["OpenAI API key in env for agent", "high", "Import returns 503 or mock mode"],
                ["Service role key used for Storage writes from API", "high", "Security misconfiguration"],
            ],
            "risks": [
                [
                    "Deep Agent non-deterministic template proposals",
                    "medium",
                    "high",
                    "Structured output validation + human approval gate",
                ],
                [
                    "Mesa isolation bugs leak cross-campaign data",
                    "low",
                    "critical",
                    "Policy layer tests per Mesa; integration tests for journey 3",
                ],
                [
                    "Large PDF uploads timeout agent job",
                    "medium",
                    "medium",
                    "Async job pattern; file size limits documented",
                ],
            ],
            "impacted_areas": [
                "app/backend/ ← new (routers per docs/product/modules.md)",
                "app/backend/agent/ ← new (sheet import runner)",
                "pyproject.toml or requirements ← update",
                "tests/backend/ ← new",
            ],
            "acceptance_criteria": [
                "AC-1: OpenAPI spec published; health + auth-protected routes respond correctly",
                "AC-2: Mesa CRUD + importing→active lifecycle enforced via API",
                "AC-3: Import endpoint accepts PDF/PNG, runs agent job, returns proposal for review",
                "AC-4: Documents CRUD respects visibility rules (master_only hidden from Player)",
                "AC-5: Character sheet create/edit stores data.json in Storage with version snapshot",
                "AC-6: Invite flow: create token, accept, join as Player; 7-day expiry enforced",
            ],
            "definition_of_done": [
                "pytest backend suite passes",
                "OpenAPI matches implemented routes",
                "Integration tests cover MVP journeys 1–3 API paths",
                "make sdlc-doctor exits 0",
                "PR merged; Plane evidence with validation output",
            ],
            "next_step": "Unblocks FRONTEND — stable OpenAPI for Mesa, import, documents, sheets.",
        }
    )


def frontend_html() -> str:
    return build_plan_html(
        {
            "task_name": "[AI][FRONTEND] Auth, Mesa bootstrap, sheet renderer, wiki",
            "story": [
                "Players and Masters interact with the RPG Platform through a React SPA in "
                "Brazilian Portuguese. Authentication uses Supabase Auth; all data flows "
                "through the FastAPI backend.",
                "This child delivers login/register (email + Google), Mesa creation with import "
                "review UI, JSON-schema-driven sheet renderer, documents/wiki with search, "
                "and role-aware navigation for Master, Player, and Admin.",
            ],
            "scope": [
                "React + Vite + TypeScript at app/frontend/; UI strings PT-BR only",
                "Supabase Auth UI integration (email + password + Google OAuth)",
                "Password reset flow; profile name/avatar",
                "Mesa create form; status importing/active indicators",
                "Sheet upload + import review (approve/reject/D&D 5e fallback)",
                "Sheet template + character renderer from JSON schema",
                "Documents/wiki list, CRUD forms, text search",
                "Role-aware nav: Master vs Player vs Admin routes",
                "Invite accept flow from email link",
            ],
            "non_goals": [
                "Backend API implementation (BACKEND child)",
                "Dice roller, maps, chat",
                "English or multi-locale i18n (PT-BR only per Q-012)",
            ],
            "assumptions": [
                ["BACKEND child provides stable /api/v1/ OpenAPI", "high", "Blocked until API ready"],
                ["Shared schemas from app/shared/ consumed by renderer", "high", "Renderer mismatch"],
                ["Supabase Auth redirect URLs configured for local dev", "medium", "OAuth broken locally"],
            ],
            "risks": [
                [
                    "JSON schema renderer complexity for custom sheet layouts",
                    "medium",
                    "high",
                    "Start with D&D 5e seed + agent output fields; iterate on widget map",
                ],
                [
                    "OAuth redirect misconfiguration in local dev",
                    "medium",
                    "medium",
                    "Document Supabase Auth URL settings in README",
                ],
            ],
            "impacted_areas": [
                "app/frontend/ ← new",
                "app/frontend/src/features/auth/ ← new",
                "app/frontend/src/features/mesas/ ← new",
                "app/frontend/src/features/sheets/ ← new",
                "app/frontend/src/features/documents/ ← new",
            ],
            "acceptance_criteria": [
                "AC-1: User can register, login (email + Google), reset password in PT-BR UI",
                "AC-2: Master creates Mesa, uploads sheet, reviews agent proposal, Mesa becomes active",
                "AC-3: Player accepts invite, sees only permitted documents, creates character sheet",
                "AC-4: Sheet renderer displays template fields from JSON schema correctly",
                "AC-5: Mesa A data invisible when user switches context to Mesa B (journey 3)",
            ],
            "definition_of_done": [
                "Frontend lint + build pass",
                "Manual or e2e smoke covers MVP journeys 1–3",
                "All UI copy PT-BR",
                "make sdlc-doctor exits 0",
                "PR merged; Plane evidence posted",
            ],
            "next_step": "QA e2e against staging/local full stack after merge.",
        }
    )


def find_by_title(issues: list[dict], title: str) -> dict | None:
    for item in issues:
        if (item.get("name") or "").strip() == title:
            return item
    return None


def main() -> int:
    api_key, workspace, project_id = board_api()
    todo_state_id = resolve_state_id(api_key, workspace, project_id, name="Todo")
    issues = list_issues(api_key, workspace, project_id)

    epic = find_by_title(issues, EPIC_TITLE)
    child_specs = [
        ("[AI][INFRA] Supabase local, shared contracts, env bootstrap", infra_html),
        (
            "[AI][BACKEND] API, auth bridge, mesas, import agent, documents, sheets",
            backend_html,
        ),
        ("[AI][FRONTEND] Auth, Mesa bootstrap, sheet renderer, wiki", frontend_html),
    ]

    if epic:
        epic_seq = epic["sequence_id"]
        epic_uuid = epic["id"]
        print(f"EXISTS: epic {format_card(epic_seq)}")
    else:
        placeholder_html = epic_html("RPG-INFRA", "RPG-BACKEND", "RPG-FRONTEND")
        epic = create_issue(
            api_key,
            workspace,
            project_id,
            name=EPIC_TITLE,
            description_html=placeholder_html,
            todo_state_id=todo_state_id,
        )
        epic_seq = epic["sequence_id"]
        epic_uuid = epic["id"]
        print(f"CREATED: epic {format_card(epic_seq)}")

    children: list[tuple[str, int, str]] = []
    for title, html_fn in child_specs:
        existing = find_by_title(issues, title)
        if existing:
            seq = existing["sequence_id"]
            uuid = existing["id"]
            print(f"EXISTS: child {format_card(seq)} — {title[:50]}")
        else:
            created = create_issue(
                api_key,
                workspace,
                project_id,
                name=title,
                description_html=html_fn(),
                parent=epic_uuid,
                todo_state_id=todo_state_id,
            )
            seq = created["sequence_id"]
            uuid = created["id"]
            print(f"CREATED: child {format_card(seq)} — {title[:50]}")
        children.append((title, seq, uuid))

    infra_id = format_card(children[0][1])
    backend_id = format_card(children[1][1])
    frontend_id = format_card(children[2][1])
    final_epic_html = epic_html(infra_id, backend_id, frontend_id)
    patch_description(api_key, workspace, project_id, epic_uuid, final_epic_html)
    print(f"UPDATED: epic task breakdown with {infra_id}, {backend_id}, {frontend_id}")

    card_script = SCRIPTS / "plane_card.py"
    rc = subprocess.run(
        [sys.executable, str(card_script), "validate-all", "--card", format_card(epic_seq)],
        cwd=ROOT,
    ).returncode
    if rc != 0:
        print("WARN: validate-all failed — review epic description", file=sys.stderr)
        return rc

    print("\n=== Summary ===")
    print(f"Epic:     {format_card(epic_seq)}")
    for title, seq, _ in children:
        print(f"Child:    {format_card(seq)} — {title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
