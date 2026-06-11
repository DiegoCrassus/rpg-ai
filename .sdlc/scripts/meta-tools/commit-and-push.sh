#!/usr/bin/env bash
# Meta-tool: commit-and-push
# Deterministic sequence: lint check → git add → commit → push
# Usage: .sdlc/scripts/meta-tools/commit-and-push.sh --card RPG-N --msg "Short imperative summary"
# Source: AWO / Meta-tools (arXiv 2601.22037)
set -euo pipefail

CARD=""
MSG=""
PATHS="."

while [[ $# -gt 0 ]]; do
  case $1 in
    --card)  CARD="$2";  shift 2 ;;
    --msg)   MSG="$2";   shift 2 ;;
    --paths) PATHS="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CARD" || -z "$MSG" ]]; then
  echo "Usage: $0 --card RPG-N --msg 'Short imperative summary' [--paths '.']" >&2
  exit 1
fi

echo "[meta] commit-and-push: card=$CARD"

# Step 1: Confirm gate is open
echo "[meta] step 1/5 — checking session gate..."
GATE_STATUS=$(python3 -c "
import sys; sys.path.insert(0, '.sdlc/dsl')
from gate import load_session_gate
g = load_session_gate()
print(g.gate_status)
")
if [[ "$GATE_STATUS" != "open" ]]; then
  echo "[meta] ERROR: gate is not open. Run validate-and-start first." >&2
  exit 1
fi

# Step 2: Quick lint (if ruff available)
echo "[meta] step 2/5 — running lint check (if available)..."
if command -v ruff &>/dev/null; then
  ruff check . --quiet || echo "[meta] lint warnings found — review before finalizing"
fi

# Step 3: Stage files
echo "[meta] step 3/5 — staging files..."
git add $PATHS

# Step 4: Commit with SDLC-standard message
FULL_MSG="[$CARD] $MSG"
echo "[meta] step 4/5 — committing: $FULL_MSG"
git commit -m "$FULL_MSG"

# Step 5: Push
echo "[meta] step 5/5 — pushing to remote..."
git push -u origin HEAD

HASH=$(git rev-parse --short HEAD)
echo "[meta] ✓ commit-and-push complete — $HASH on $(git rev-parse --abbrev-ref HEAD)"
