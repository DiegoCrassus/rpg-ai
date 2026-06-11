# Skill: Secrets Management

## Purpose

Ensure no secrets (API keys, passwords, tokens, certificates) are committed to the repository, using automatic verification on every commit and every PR.

## When to use

- As pre-commit hook on every development machine
- As mandatory CI gate before any other check
- When reviewing PRs that change configuration or infrastructure files

## Required inputs

- PR diff or staged files for commit
- `.gitleaks.toml` (custom rules — optional)
- Allowlist for known false positives

## Procedure

### Pre-commit (local)

```bash
# Install gitleaks
brew install gitleaks
# or: pip install gitleaks-python / download binary

# Configure pre-commit hook (.git/hooks/pre-commit)
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
gitleaks protect --staged --redact --exit-code 1
if [ $? -ne 0 ]; then
  echo "ERROR: Secret detected in staged diff. Remove before committing."
  exit 1
fi
EOF
chmod +x .git/hooks/pre-commit
```

### CI (per PR)

```bash
# Scan entire repository
gitleaks detect --source . \
  --report-format json \
  --report-path gitleaks-report.json \
  --redact \
  --exit-code 1

# Scan PR diff only
gitleaks detect --source . \
  --log-opts="origin/develop..HEAD" \
  --report-format json \
  --exit-code 1
```

### Automatically detected patterns

| Type | Examples |
|------|---------|
| AWS keys | `AKIA...`, `aws_secret_access_key` |
| GitHub tokens | `ghp_`, `github_pat_` |
| OpenAI keys | `sk-proj-`, `sk-` |
| Stripe keys | `sk_live_`, `pk_live_` |
| Private keys | `-----BEGIN RSA PRIVATE KEY-----` |
| Database URLs | `postgres://user:password@host` |
| JWT secrets | `JWT_SECRET=`, `SECRET_KEY=` |
| Any pattern `= "sk-"`, `= "key-"` | Generic heuristic |

## .env rules

- `.env` must be in `.gitignore` — never committed
- `.env.example` must contain only keys without real values
- Comment in `.env.example` which service each variable belongs to

```bash
# Verify .env is ignored
git check-ignore .env || echo "WARNING: .env is not in .gitignore"

# Verify .env.example has no real values
grep -E "=.{8,}" .env.example | grep -v "^#" | grep -v "=your_" | grep -v "=<" | grep -v "=placeholder"
```

## Outputs

- `gitleaks-report.json` with all findings
- List of files + lines where secrets were detected
- Exit code: 0 (clean) or 1 (secret detected)

## Validation checklist

- [ ] Pre-commit hook installed and working
- [ ] `.env` is in `.gitignore`
- [ ] `.env.example` contains no real values
- [ ] CI gitleaks gate active in workflow
- [ ] No `console.log()` or `print()` exposing environment variables

## Failure modes

| Failure | Immediate action |
|-------|---------------|
| Secret found in diff | Remove from code, revoke credential, force push if necessary |
| Secret found in old commit | `git filter-repo` to remove from history + revoke |
| False positive blocking CI | Add to allowlist in `.gitleaks.toml` with justification |
| `.env` committed accidentally | Remove from history immediately + revoke all credentials in file |
