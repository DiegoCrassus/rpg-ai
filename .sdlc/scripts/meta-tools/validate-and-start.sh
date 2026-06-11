#!/usr/bin/env bash
# Meta-tool: validate-and-start
# Deterministic sequence: Plane validate → gate check → branch checkout
# Usage: .sdlc/scripts/meta-tools/validate-and-start.sh --card RPG-N --slug my-feature --stage implementation
# Source: AWO / Meta-tools (arXiv 2601.22037)
set -euo pipefail

CARD=""
SLUG=""
STAGE="implementation"

while [[ $# -gt 0 ]]; do
  case $1 in
    --card)  CARD="$2";  shift 2 ;;
    --slug)  SLUG="$2";  shift 2 ;;
    --stage) STAGE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CARD" || -z "$SLUG" ]]; then
  echo "Usage: $0 --card RPG-N --slug my-feature [--stage implementation]" >&2
  exit 1
fi

echo "[meta] validate-and-start: card=$CARD slug=$SLUG stage=$STAGE"

# Step 1: Validate Plane card is ready
echo "[meta] step 1/4 — validating Plane card..."
python3 .sdlc/scripts/plane_card.py validate-all --card "$CARD"

# Step 2: Run discovery hook
echo "[meta] step 2/4 — running discovery hook..."
python3 .sdlc/scripts/discovery_hook.py

# Step 3: Open session gate
echo "[meta] step 3/4 — opening session gate..."
python3 .sdlc/dsl/cli.py workflow start --card "$CARD" --slug "$SLUG" --stage "$STAGE"

# Step 4: Confirm branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "[meta] step 4/4 — on branch: $BRANCH"
echo "[meta] ✓ validate-and-start complete — gate open for $CARD on $BRANCH"
