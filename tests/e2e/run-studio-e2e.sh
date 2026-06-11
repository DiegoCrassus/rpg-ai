#!/usr/bin/env bash
# Start Studio API + UI preview, run Playwright smoke + builder E2E, then tear down.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
API_PORT="${STUDIO_API_PORT:-8100}"
UI_PORT="${STUDIO_UI_PORT:-5174}"
API_PID=""
UI_PID=""

pick_free_port() {
  local port
  for port in "$@"; do
    if ! ss -tln 2>/dev/null | grep -q ":${port} "; then
      echo "$port"
      return
    fi
  done
  echo "$1"
}

cleanup() {
  if [[ -n "$API_PID" ]]; then kill "$API_PID" 2>/dev/null || true; fi
  if [[ -n "$UI_PID" ]]; then kill "$UI_PID" 2>/dev/null || true; fi
}
trap cleanup EXIT INT TERM

cd "$ROOT/app/studio-frontend"
npm run build

API_PORT="$(pick_free_port "${API_PORT}" 8102 8110)"
UI_PORT="$(pick_free_port "${UI_PORT}" 5175 5180)"
cd "$ROOT"
STUDIO_REPO_ROOT="$ROOT" PYTHONPATH="$ROOT/app/studio-backend/src:$ROOT" \
  python3 -m uvicorn studio_service.main:app --host 127.0.0.1 --port "$API_PORT" &
API_PID=$!
sleep 1
if ! kill -0 "$API_PID" 2>/dev/null; then
  echo "Studio API failed to start on port ${API_PORT}" >&2
  exit 1
fi

cd "$ROOT/app/studio-frontend"
VITE_STUDIO_API_URL="http://127.0.0.1:${API_PORT}" npm run preview -- --host 127.0.0.1 --port "$UI_PORT" &
UI_PID=$!

for _ in $(seq 1 60); do
  if curl -sf "http://127.0.0.1:${API_PORT}/studio/health" >/dev/null \
    && curl -sf "http://127.0.0.1:${UI_PORT}/" >/dev/null; then
    break
  fi
  sleep 0.5
done

curl -sf "http://127.0.0.1:${API_PORT}/studio/health" >/dev/null
curl -sf "http://127.0.0.1:${UI_PORT}/" >/dev/null

cd "$ROOT/tests/e2e"
if [[ ! -d node_modules ]]; then
  npm install
fi
if [[ ! -d node_modules/.cache/ms-playwright ]] && [[ -z "${PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD:-}" ]]; then
  npx playwright install chromium
fi

STUDIO_UI_URL="http://127.0.0.1:${UI_PORT}" npm test
