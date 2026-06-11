#!/usr/bin/env bash
# Meta-tool: qa-to-review
# Deterministic sequence: run tests → make sdlc-doctor → write QA evidence
# Usage: .sdlc/scripts/meta-tools/qa-to-review.sh --card RPG-N [--test-cmd "pytest"]
# Source: AWO / Meta-tools (arXiv 2601.22037)
set -euo pipefail

CARD=""
TEST_CMD="pytest"
EVIDENCE_FILE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --card)      CARD="$2";       shift 2 ;;
    --test-cmd)  TEST_CMD="$2";   shift 2 ;;
    --evidence)  EVIDENCE_FILE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CARD" ]]; then
  echo "Usage: $0 --card RPG-N [--test-cmd 'pytest'] [--evidence path/to/evidence.json]" >&2
  exit 1
fi

EVIDENCE_FILE="${EVIDENCE_FILE:-.sdlc/memory/qa-evidence-$CARD.json}"
echo "[meta] qa-to-review: card=$CARD test_cmd=$TEST_CMD"

# Step 1: Run tests
echo "[meta] step 1/4 — running tests: $TEST_CMD"
set +e
TEST_OUTPUT=$($TEST_CMD 2>&1)
TEST_EXIT=$?
set -e
echo "$TEST_OUTPUT"
TESTS_PASS=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= passed)' | tail -1 || echo "0")
TESTS_FAIL=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= failed)' | tail -1 || echo "0")
echo "[meta] tests: passed=$TESTS_PASS failed=$TESTS_FAIL"

# Step 2: Run Doctor
echo "[meta] step 2/4 — running SDLC Doctor..."
set +e
DOCTOR_OUTPUT=$(make sdlc-doctor 2>&1)
DOCTOR_EXIT=$?
set -e
echo "$DOCTOR_OUTPUT"
DOCTOR_SUMMARY=$(echo "$DOCTOR_OUTPUT" | grep "Doctor summary" | tail -1)

# Step 3: Write QA evidence
echo "[meta] step 3/4 — writing QA evidence to $EVIDENCE_FILE"
cat > "$EVIDENCE_FILE" <<EOF
{
  "card": "$CARD",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "tests": {
    "command": "$TEST_CMD",
    "exit_code": $TEST_EXIT,
    "passed": $TESTS_PASS,
    "failed": $TESTS_FAIL
  },
  "doctor": {
    "exit_code": $DOCTOR_EXIT,
    "summary": "$DOCTOR_SUMMARY"
  },
  "verdict": "$([ $TEST_EXIT -eq 0 ] && [ $DOCTOR_EXIT -eq 0 ] && echo "PASS" || echo "FAIL")"
}
EOF
cat "$EVIDENCE_FILE"

# Step 4: Final summary
echo "[meta] step 4/4 — QA summary"
if [[ $TEST_EXIT -eq 0 && $DOCTOR_EXIT -eq 0 ]]; then
  echo "[meta] ✓ qa-to-review complete — PASS — ready for Reviewer"
else
  echo "[meta] ✗ qa-to-review FAIL — tests=$TESTS_FAIL failed, doctor=$DOCTOR_EXIT"
  echo "[meta] Fix failures before delegating to Reviewer"
  exit 1
fi
