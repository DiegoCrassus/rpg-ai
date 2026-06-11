# Skill: Branch Naming

## Purpose

Ensure every branch created in the repository has a meaningful, traceable, consistent name, always linked to the originating task or Issue.

## When to use

- Before creating any branch
- When reviewing whether an existing branch follows the convention
- When suggesting a branch name in an Issue triage comment (Issue Analyst)
- When starting any task (Implementer)

## Fundamental rule

> **Every branch must reference the work it is associated with.**
> No branch without traceability to a Plane task or GitHub Issue is allowed.

---

## General format

```
<prefix>/<references>-<descriptive-slug>
```

### Valid prefixes

| Prefix | When to use |
|---------|-------------|
| `feature/` | New functionality (did not exist before) |
| `bugfix/` | Confirmed bug fix |
| `hotfix/` | Urgent production fix |
| `docs/` | Documentation only (no production code) |
| `infra/` | Infrastructure, tooling, CI/CD, observability |
| `refactor/` | Refactor without external behavior change |
| `sdlc/` | Changes in `.sdlc/`, `.cursor/`, `Makefile`, governance |
| `test/` | Test addition or fix only |

---

## Reference patterns

### Case 1 — Plane task (no GitHub Issue)

```
<prefix>/INVESTIMENTS-<N>-<slug>
```

Examples:
```
feature/RPGTIMENTS-12-add-plane-endpoint
bugfix/INVESTIMENTS-15-fix-token-count
docs/INVESTIMENTS-18-update-arch-overview
infra/INVESTIMENTS-21-setup-obs-server
```

### Case 2 — GitHub Issue (no prior Plane task)

```
<prefix>/issue-gh-<N>-<slug>
```

Examples:
```
bugfix/issue-gh-42-fix-null-token-count
feature/issue-gh-58-add-plane-webhook
docs/issue-gh-63-update-local-dev-guide
```

### Case 3 — Plane task + linked GitHub Issue (most common)

```
<prefix>/INVESTIMENTS-<N>-issue-gh-<N>-<slug>
```

Examples:
```
bugfix/INVESTIMENTS-15-issue-gh-42-fix-token-count
feature/RPGTIMENTS-20-issue-gh-58-add-plane-endpoint
infra/INVESTIMENTS-21-issue-gh-61-add-obs-server
```

### Case 4 — Urgent hotfix (no time to create Plane card first)

```
hotfix/issue-gh-<N>-<slug>
```

> Create the Plane card retrospectively as soon as possible.

---

## Slug rules

| Rule | Correct | Wrong |
|-------|---------|--------|
| Lowercase letters only | `add-endpoint` | `AddEndpoint` |
| Words separated by hyphen | `fix-token-count` | `fix_token_count` |
| Maximum 5 words | `add-plane-work-item-api` | `add-the-new-plane-work-item-api-endpoint` |
| English | `add-endpoint` | `adicionar-endpoint` |
| Imperative (action + object) | `add-endpoint`, `fix-null-check` | `endpoint`, `nullfix` |
| No articles or prepositions | `add-plane-endpoint` | `add-the-plane-endpoint` |
| No arbitrary numbers | `add-endpoint` | `add-endpoint-v2` (use card ID) |

---

## Creation procedure

```bash
# 1. Confirm Plane card ID (project investiments)
#    Ex: INVESTIMENTS-20

# 2. Confirm GitHub Issue number (if any)
#    Ex: GH #58

# 3. Build name per pattern
BRANCH="feature/RPGTIMENTS-20-issue-gh-58-add-plane-endpoint"

# 4. Create from updated develop
git checkout develop
git pull origin develop
git checkout -b "$BRANCH"

# 5. Confirm branch was created correctly
git branch --show-current
```

---

## Branch lifecycle

```
develop (base)
   │
   └─► branch created ────────────────────────────────────┐
       │                                                  │
       │  commits per subtask                            │
       │                                                  │
       └─► PR opened (draft)                             │
           │                                             │
           │  QA + Doctor + Review                       │
           │                                             │
           ├─► PR APPROVED → squash merge → develop      │
           │   └─► branch DELETED automatically          │
           │                                             │
           └─► PR CLOSED (rejected)                      │
               └─► branch DELETED by DevOps              │
                                                          │
       NO branch left orphaned ──────────────────────────┘
```

---

## Branch deletion rules

### On merge (approved PR)

1. PR **must** have `delete_branch_on_merge: true` at creation time
2. GitHub deletes the branch automatically after squash merge
3. DevOps confirms deletion via `git branch -r` or MCP `git.listBranches`

### On close without merge (rejected PR)

1. DevOps closes PR via `pulls.update(state: closed)`
2. Delete source branch immediately:
   ```bash
   git push origin --delete <branch-name>
   ```
   or via MCP `git.deleteBranch`
3. Document closure reason on the PR before closing

### Periodic check (Doctor)

Doctor checks for remote branches without an associated PR for more than 7 days and emits `[WARN] Orphan branch: <name>`.

---

## Validation checklist

- [ ] Correct prefix for work type
- [ ] Reference to Plane card (`INVESTIMENTS-N`) if it exists
- [ ] Reference to GitHub Issue (`issue-gh-N`) if it exists
- [ ] Slug in English, kebab-case, max 5 words, imperative
- [ ] Branch created from updated `develop`
- [ ] `delete_branch_on_merge: true` set on PR

---

## Failure modes

| Problem | Cause | Solution |
|----------|-------|---------|
| Branch without prefix | Manual creation without reading skill | Rename or recreate |
| Branch without traceability | Issue/card not identified | Create Plane card, rename branch |
| Slug too long | Lack of synthesis | Use only noun + key verb |
| Branch directly on main/develop | No review | Revert immediately, open PR |
| Orphan branch after PR closed | DevOps did not delete | Delete via MCP or CLI |
