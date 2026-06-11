# Skill: Plane Formatting & Evidence

> **Authority:** `.sdlc/process/change-lifecycle.md` · `.sdlc/scripts/plane_html.py`

## Problem

Plane uses **TipTap** HTML. Raw tags like `<div><h2>Story</h2><p>…` render poorly.
Completion comments must carry **technical context** for future agents — not one-line stubs.

## Description HTML (plans)

Use `.sdlc/scripts/plane_html.py`:

| Element | Required class |
|---------|----------------|
| Headings | `class="editor-heading-block"` |
| Paragraphs | `class="editor-paragraph-block"` |
| Bullet lists | `class="list-disc pl-7 space-y-(--list-spacing-y) tight"` |
| Tables | Plane `<table><tbody><tr>…` structure |
| DoD checkboxes | `data-type="taskList"` / `taskItem` |

**Create plans:**

```python
from plane_html import build_plan_html, document
html = build_plan_html({...})
```

**Upgrade legacy cards:**

```bash
python3 .sdlc/scripts/plane_card.py reformat-description --card RPG-N
python3 .sdlc/scripts/plane_card.py reformat-all   # RPG-19..24
```

**Never** paste markdown-only or unstyled HTML into `description_html`.

## Completion evidence (Done)

Structured JSON → rich comment via `plane_evidence.build_completion_evidence`.

### Required sections

1. **Summary** — one paragraph
2. **Problems Solved** — bullets (why the task existed)
3. **Technical Delivery** — endpoints, modules, stack, files
4. **Validation Evidence** — pytest, doctor, CI (real output)
5. **Artifacts** — PR, branch, commit, docs
6. **Context for Future Work** — what downstream tasks must know

Template: `.sdlc/templates/plane/evidence-template.json` (copy/fill per card).

### Post evidence

```bash
python3 .sdlc/scripts/plane_card.py post-evidence \
  --card RPG-20 \
  --file .sdlc/templates/plane/evidence-template.json
```

On **finish-change** / **auto_merge_pr**:

```bash
python3 .sdlc/scripts/auto_merge_pr.py --pr 32 --card RPG-20 \
  --plane-comment --evidence-file .sdlc/templates/plane/evidence-template.json
```

If `--evidence-file` omitted, auto_merge looks for `.sdlc/templates/plane/evidence-{CARD}.json`.

### In Progress comment

```bash
python3 .sdlc/scripts/plane_state.py in-progress --card RPG-N --branch feature/RPG-N-slug
```

Uses formatted `build_start_comment` HTML.

## Planner / Implementer handoff

- **Planner:** persist plans with `build_plan_html` or MCP using formatted HTML
- **Implementer:** before finish-change, fill evidence JSON (problems_solved + context_for_future mandatory)
- **Reviewer:** reject Done if evidence lacks technical sections

## Prohibitions

- Plain `<p>PR #32</p>` as sole Done evidence
- Markdown in `description_html` without TipTap classes
- Local `specs/` copies of Plane content
