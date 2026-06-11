"""Plane TipTap-compatible HTML builder for work item bodies and comments.

Plane's editor expects CSS classes such as editor-heading-block and
editor-paragraph-block. Raw <div><h2> markup renders poorly in the UI.
"""

from __future__ import annotations

import html
import re
from collections.abc import Iterable


def _esc(text: str) -> str:
    return html.escape(str(text), quote=False)


def heading(text: str, level: int = 2) -> str:
    tag = f"h{min(max(level, 1), 3)}"
    cls = "editor-heading-block"
    return f'<{tag} class="{cls}">{_esc(text)}</{tag}>'


def paragraph(text: str) -> str:
    return f'<p class="editor-paragraph-block">{text}</p>'


def paragraph_text(text: str) -> str:
    return paragraph(_esc(text))


def inline_code(text: str) -> str:
    return f"<code>{_esc(text)}</code>"


def link(label: str, url: str) -> str:
    return f'<a href="{_esc(url)}" target="_blank" rel="noopener noreferrer">{_esc(label)}</a>'


def bullet_list(items: Iterable[str], *, escape: bool = True) -> str:
    lis = []
    for item in items:
        body = _esc(item) if escape else item
        lis.append(
            f'<li class="not-prose space-y-2"><p class="editor-paragraph-block">{body}</p></li>'
        )
    return f'<ul class="list-disc pl-7 space-y-(--list-spacing-y) tight">{"".join(lis)}</ul>'


def task_list(items: Iterable[tuple[str, bool]]) -> str:
    """Checkbox task list (checked state visual only in Plane)."""
    nodes = []
    for label, checked in items:
        state = "true" if checked else "false"
        nodes.append(
            '<li class="relative" data-checked="'
            f'{state}" data-type="taskItem"><label><input type="checkbox">'
            f'<span></span></label><div><p class="editor-paragraph-block">'
            f"{_esc(label)}</p></div></li>"
        )
    return f'<ul class="not-prose pl-2 space-y-2" data-type="taskList">{"".join(nodes)}</ul>'


def horizontal_rule() -> str:
    return '<div class="py-4 border-subtle" data-type="horizontalRule"><div></div></div>'


def table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(
        f'<th colspan="1" rowspan="1" background="none" hidecontent="false" class="">'
        f'<p class="editor-paragraph-block">{_esc(h)}</p></th>'
        for h in headers
    )
    body_rows = []
    for row in rows:
        cells = "".join(
            f'<td colspan="1" rowspan="1" hidecontent="false" class="">'
            f'<p class="editor-paragraph-block">{_esc(c)}</p></td>'
            for c in row
        )
        body_rows.append(f"<tr style=\"\">{cells}</tr>")
    return f"<table><tbody><tr style=\"\">{head}</tr>{''.join(body_rows)}</tbody></table>"


def blockquote(text: str) -> str:
    return f"<blockquote><p class=\"editor-paragraph-block\">{_esc(text)}</p></blockquote>"


def document(*parts: str) -> str:
    """Wrap sections in a root div (Plane convention)."""
    return f"<div>{''.join(parts)}</div>"


def convert_legacy_description(html_in: str) -> str:
    """Upgrade raw h2/p/ul/table HTML to TipTap classes."""
    if "editor-heading-block" in html_in:
        return html_in

    text = html_in.strip()
    if text.startswith("<div>"):
        text = text[5:]
        if text.endswith("</div>"):
            text = text[:-6]

    # Split on h2 sections
    sections = re.split(r"<h2[^>]*>(.*?)</h2>", text, flags=re.I | re.S)
    if len(sections) <= 1:
        return document(paragraph(re.sub(r"<[^>]+>", "", text)[:5000]))

    out: list[str] = []
    if sections[0].strip():
        out.append(_convert_fragment(sections[0]))

    for i in range(1, len(sections), 2):
        title = re.sub(r"<[^>]+>", "", sections[i]).strip()
        body = sections[i + 1] if i + 1 < len(sections) else ""
        out.append(heading(title))
        out.append(_convert_fragment(body))

    return document(*out)


def _convert_fragment(fragment: str) -> str:
    parts: list[str] = []
    fragment = fragment.strip()
    if not fragment:
        return ""

    # Tables
    for tbl in re.findall(r"<table[^>]*>.*?</table>", fragment, flags=re.I | re.S):
        headers = [
            re.sub(r"<[^>]+>", "", th).strip()
            for th in re.findall(r"<th[^>]*>(.*?)</th>", tbl, flags=re.I | re.S)
        ]
        rows = []
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", tbl, flags=re.I | re.S):
            if "<th" in tr:
                continue
            cells = [
                re.sub(r"<[^>]+>", "", td).strip()
                for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, flags=re.I | re.S)
            ]
            if cells:
                rows.append(cells)
        if headers:
            parts.append(table(headers, rows))
        fragment = fragment.replace(tbl, "", 1)

    # Lists
    for ul in re.findall(r"<ul[^>]*>(.*?)</ul>", fragment, flags=re.I | re.S):
        items = [
            re.sub(r"<[^>]+>", "", li).strip()
            for li in re.findall(r"<li[^>]*>(.*?)</li>", ul, flags=re.I | re.S)
        ]
        items = [i for i in items if i]
        if items:
            parts.append(bullet_list(items))
        fragment = fragment.replace(ul, "", 1)

    # Paragraphs and loose text
    for p in re.findall(r"<p[^>]*>(.*?)</p>", fragment, flags=re.I | re.S):
        inner = p.strip()
        if inner:
            if "<code>" in inner or "<a " in inner:
                parts.append(paragraph(inner))
            else:
                parts.append(paragraph_text(re.sub(r"<[^>]+>", "", inner)))

    remainder = re.sub(r"<[^>]+>", "", fragment).strip()
    if remainder and not parts:
        parts.append(paragraph_text(remainder))

    return "".join(parts)


def build_plan_html(sections: dict[str, str | list[str] | list[list[str]]]) -> str:
    """Build a full plan body from structured sections.

    sections keys: task_name, story (str|list), scope, non_goals, assumptions (table rows),
    risks (table rows), impacted_areas, acceptance_criteria, definition_of_done, next_step
    """
    parts: list[str] = []

    if task_name := sections.get("task_name"):
        parts.append(heading("Task Name"))
        parts.append(paragraph(inline_code(str(task_name))))

    if story := sections.get("story"):
        parts.append(heading("Story"))
        if isinstance(story, list):
            for para in story:
                parts.append(paragraph_text(str(para)))
        else:
            parts.append(paragraph_text(str(story)))

    for key, title in (
        ("scope", "Scope"),
        ("non_goals", "Non-Goals"),
        ("impacted_areas", "Impacted Areas"),
        ("acceptance_criteria", "Acceptance Criteria"),
    ):
        if val := sections.get(key):
            parts.append(heading(title))
            if isinstance(val, list) and val and isinstance(val[0], str):
                parts.append(bullet_list(val))
            elif isinstance(val, str):
                parts.append(paragraph_text(val))

    if assumptions := sections.get("assumptions"):
        parts.append(heading("Assumptions"))
        if isinstance(assumptions, list):
            parts.append(table(["Assumption", "Confidence", "Impact if wrong"], assumptions))

    if risks := sections.get("risks"):
        parts.append(heading("Risks"))
        if isinstance(risks, list):
            parts.append(
                table(["Risk", "Likelihood", "Impact", "Mitigation"], risks)
            )

    if dod := sections.get("definition_of_done"):
        parts.append(heading("Definition of Done"))
        if isinstance(dod, list):
            parts.append(task_list([(str(x), False) for x in dod]))

    if nxt := sections.get("next_step"):
        parts.append(heading("Next Step"))
        parts.append(paragraph_text(str(nxt)))

    return document(*parts)
