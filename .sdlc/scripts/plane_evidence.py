"""Structured completion evidence for Plane work items."""

from __future__ import annotations

from typing import Any

from plane_html import (
    bullet_list,
    document,
    heading,
    horizontal_rule,
    inline_code,
    link,
    paragraph_text,
    table,
)


def build_completion_evidence(data: dict[str, Any]) -> str:
    """Render rich Done evidence comment (HTML) from structured dict.

    Expected keys:
      card, title, summary, problems_solved (list), technical (dict),
      validation (dict), artifacts (dict), context_for_future (list)
    """
    card = data.get("card", "RPG-N")
    title = data.get("title", "")
    summary = data.get("summary", "")

    parts: list[str] = [
        heading(f"Done — {card}"),
        paragraph_text(title) if title else "",
    ]
    if summary:
        parts.append(paragraph_text(f"Summary: {summary}"))
    parts.append(horizontal_rule())

    if problems := data.get("problems_solved"):
        parts.append(heading("Problems Solved"))
        parts.append(bullet_list([str(p) for p in problems]))

    tech = data.get("technical") or {}
    if tech:
        parts.append(heading("Technical Delivery"))
        tech_bullets = []
        if endpoints := tech.get("endpoints"):
            tech_bullets.append(f"Endpoints: {', '.join(endpoints)}")
        if modules := tech.get("modules"):
            tech_bullets.append(f"Modules: {', '.join(modules)}")
        if stack := tech.get("stack"):
            tech_bullets.append(f"Stack: {stack}")
        if decisions := tech.get("decisions"):
            tech_bullets.extend(decisions)
        if tech_bullets:
            parts.append(bullet_list(tech_bullets))
        if files := tech.get("files_changed"):
            parts.append(paragraph_text("Files changed (high level):"))
            parts.append(bullet_list(files[:25]))

    val = data.get("validation") or {}
    if val:
        parts.append(heading("Validation Evidence"))
        rows = [[k, str(v)] for k, v in val.items()]
        parts.append(table(["Check", "Result"], rows))

    art = data.get("artifacts") or {}
    if art:
        parts.append(heading("Artifacts"))
        art_items = []
        if pr := art.get("pr"):
            url = art.get("pr_url") or f"https://github.com/DiegoCrassus/sdlc-ai/pull/{pr}"
            art_items.append(f"Pull Request: {link(f'#{pr}', url)}")
        if branch := art.get("branch"):
            art_items.append(f"Branch: {inline_code(branch)}")
        if commit := art.get("commit"):
            art_items.append(f"Merge commit: {inline_code(commit)}")
        if docs := art.get("docs"):
            art_items.append(f"Docs: {', '.join(docs)}")
        parts.append(bullet_list(art_items, escape=False))

    if future := data.get("context_for_future"):
        parts.append(heading("Context for Future Work"))
        parts.append(bullet_list([str(c) for c in future]))

    parts.append(horizontal_rule())
    parts.append(
        paragraph_text(
            "SDLC completion evidence · auto-generated · retain for downstream agents"
        )
    )

    return document(*[p for p in parts if p])


def build_start_comment(card: str, branch: str, agent: str = "implementer") -> str:
    from plane_html import document, heading, paragraph_text, table

    return document(
        heading(f"In Progress — {card}"),
        paragraph_text("Work started per start-change skill."),
        table(
            ["Field", "Value"],
            [
                ["Branch", branch],
                ["Agent", agent],
                ["Gate", "Plane state → In Progress before code"],
            ],
        ),
    )


def _esc(text: str) -> str:
    import html

    return html.escape(str(text), quote=False)
