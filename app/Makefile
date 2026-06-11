# RPG Platform — local stack (install | infra | start | stop)
#
# From repo root:  make -C app <target>
# From app/:      make <target>

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
BACKEND_SRC := $(ROOT)/app/backend/src
FRONTEND := $(ROOT)/app/frontend
SUPABASE_DIR := $(ROOT)/app/infra/supabase
RUN_DIR := $(ROOT)/app/.run
E2E_DIR := $(ROOT)/tests/e2e

API_PORT ?= 8000
UI_PORT ?= 5173
SUPABASE_PORTS := 54321 54322 54323 54324
APP_PORTS := $(API_PORT) $(UI_PORT)
ALL_PORTS := $(APP_PORTS) $(SUPABASE_PORTS)

PYTHON ?= $(shell if [ -x $(ROOT)/.venv/bin/python ]; then echo $(ROOT)/.venv/bin/python; elif command -v python3 >/dev/null 2>&1; then echo python3; else echo python; fi)
VENV_PY := $(ROOT)/.venv/bin/python
VENV_PIP := $(ROOT)/.venv/bin/pip

.PHONY: help install migrate infra start stop test build contracts e2e \
        _ensure-supabase-cli _ensure-docker _env-check _port-busy

help:
	@echo "RPG Platform (app/)"
	@echo ""
	@echo "  make install   Python venv + backend deps + frontend npm"
	@echo "  make migrate   Apply SQL migrations (supabase db reset, local)"
	@echo "  make infra     Supabase local stack (installs CLI if missing)"
	@echo "  make start     infra + API :$(API_PORT) + UI :$(UI_PORT) (background)"
	@echo "  make stop      Stop API, UI, Supabase; verify ports released"
	@echo ""
	@echo "Dev admin (after migrate): admin@rpg.local / RpgAdmin!local"
	@echo ""
	@echo "Other:"
	@echo "  make test      pytest backend + shared + vitest frontend"
	@echo "  make build     frontend production build"
	@echo "  make contracts validate JSON schemas"
	@echo ""
	@echo "Setup: cp $(ROOT)/.env.example $(ROOT)/.env"
	@echo "       cp $(FRONTEND)/.env.example $(FRONTEND)/.env"
	@echo "After infra: copy Supabase keys from CLI output into .env files"

# ---------------------------------------------------------------------------
# install
# ---------------------------------------------------------------------------

install:
	@test -x $(VENV_PY) || $(PYTHON) -m venv $(ROOT)/.venv
	@$(VENV_PIP) install -e "$(ROOT)[dev,agent]"
	@cd $(FRONTEND) && npm install
	@echo "OK: install complete"

# ---------------------------------------------------------------------------
# migrate — apply Supabase SQL migrations (local reset)
# ---------------------------------------------------------------------------

migrate: _ensure-docker _ensure-supabase-cli
	@echo "==> Applying migrations (supabase db reset — local only, wipes DB)"
	@SUPABASE_BIN=$$(command -v supabase 2>/dev/null || echo "$$HOME/.local/bin/supabase"); \
	  cd $(SUPABASE_DIR) && $$SUPABASE_BIN db reset --yes
	@$(PYTHON) $(ROOT)/app/scripts/sync_env_from_supabase.py
	@echo "OK: migrations applied"
	@echo "    Admin: admin@rpg.local / RpgAdmin!local"

# ---------------------------------------------------------------------------
# infra — Supabase (+ prerequisites)
# ---------------------------------------------------------------------------

infra: _ensure-docker _ensure-supabase-cli
	@echo "==> Supabase ($(SUPABASE_DIR))"
	@SUPABASE_BIN=$$(command -v supabase 2>/dev/null || echo "$$HOME/.local/bin/supabase"); \
	  cd $(SUPABASE_DIR) && \
	  if $$SUPABASE_BIN status 2>/dev/null | grep -qE 'API URL|Project URL'; then \
	    echo "OK: Supabase already running"; \
	    $$SUPABASE_BIN status; \
	  else \
	    $$SUPABASE_BIN start; \
	  fi
	@$(PYTHON) $(ROOT)/app/scripts/sync_env_from_supabase.py
	@echo "OK: infra ready (API :54321, Studio :54323)"

_ensure-docker:
	@docker info >/dev/null 2>&1 || { \
	  echo "ERROR: Docker not running."; \
	  echo "Start Docker Desktop and enable WSL integration."; \
	  exit 1; \
	}

_ensure-supabase-cli:
	@SUPABASE_BIN=$$(command -v supabase 2>/dev/null || echo "$$HOME/.local/bin/supabase"); \
	  if [ ! -x "$$SUPABASE_BIN" ]; then \
	    echo "==> Installing Supabase CLI to ~/.local/bin ..."; \
	    mkdir -p "$$HOME/.local/bin"; \
	    npm install -g supabase@latest --prefix "$$HOME/.local" || exit 1; \
	    SUPABASE_BIN="$$HOME/.local/bin/supabase"; \
	  fi; \
	  "$$SUPABASE_BIN" --version >/dev/null || { echo "ERROR: supabase CLI broken"; exit 1; }

_env-check:
	@if [ ! -f $(ROOT)/.env ]; then \
	  echo "ERROR: missing $(ROOT)/.env — run make infra (syncs from Supabase)"; \
	  exit 1; \
	fi
	@if grep -E '^DATABASE_URL=.*sqlite' $(ROOT)/.env >/dev/null 2>&1; then \
	  echo "ERROR: .env DATABASE_URL still points to SQLite."; \
	  echo "Run: make infra   (auto-syncs Supabase Postgres URL)"; \
	  exit 1; \
	fi
	@if ! grep -E '^DATABASE_URL=.*(postgresql|postgres)' $(ROOT)/.env >/dev/null 2>&1; then \
	  echo "ERROR: .env missing PostgreSQL DATABASE_URL."; \
	  echo "Run: make infra"; \
	  exit 1; \
	fi
	@grep -q '^SUPABASE_JWT_SECRET=.\+' $(ROOT)/.env || { \
	  echo "ERROR: SUPABASE_JWT_SECRET empty in .env — run make infra"; exit 1; }

# ---------------------------------------------------------------------------
# start — infra + backend + frontend
# ---------------------------------------------------------------------------

start: infra _env-check
	@test -x $(VENV_PY) || (echo "ERROR: run make install first" && exit 1)
	@test -f $(FRONTEND)/node_modules/vite/bin/vite.js || (echo "ERROR: run make install first" && exit 1)
	@mkdir -p $(RUN_DIR)
	@echo "==> API :$(API_PORT)"
	@if [ -f $(RUN_DIR)/api.pid ] && kill -0 $$(cat $(RUN_DIR)/api.pid) 2>/dev/null; then \
	  echo "    already running (pid $$(cat $(RUN_DIR)/api.pid))"; \
	else \
	  cd $(ROOT) && PYTHONPATH=$(BACKEND_SRC) nohup $(VENV_PY) -m uvicorn rpg_platform.main:app \
	    --reload --host 127.0.0.1 --port $(API_PORT) \
	    > $(RUN_DIR)/api.log 2>&1 & echo $$! > $(RUN_DIR)/api.pid; \
	fi
	@echo "==> UI :$(UI_PORT)"
	@if [ -f $(RUN_DIR)/ui.pid ] && kill -0 $$(cat $(RUN_DIR)/ui.pid) 2>/dev/null; then \
	  echo "    already running (pid $$(cat $(RUN_DIR)/ui.pid))"; \
	else \
	  cd $(FRONTEND) && nohup npm run dev -- --host 127.0.0.1 --port $(UI_PORT) \
	    > $(RUN_DIR)/ui.log 2>&1 & echo $$! > $(RUN_DIR)/ui.pid; \
	fi
	@echo "==> Waiting for health ..."
	@ok=0; for _ in $$(seq 1 40); do \
	  curl -sf "http://127.0.0.1:$(API_PORT)/api/v1/health" >/dev/null && ok=1 && break; \
	  sleep 0.5; \
	done; \
	if [ "$$ok" != "1" ]; then \
	  echo "ERROR: API not healthy on :$(API_PORT) — see $(RUN_DIR)/api.log"; \
	  tail -20 $(RUN_DIR)/api.log 2>/dev/null || true; \
	  exit 1; \
	fi; \
	ok=0; for _ in $$(seq 1 40); do \
	  curl -sf "http://127.0.0.1:$(UI_PORT)/" >/dev/null && ok=1 && break; \
	  sleep 0.5; \
	done; \
	if [ "$$ok" != "1" ]; then \
	  echo "ERROR: UI not reachable on :$(UI_PORT) — see $(RUN_DIR)/ui.log"; \
	  tail -20 $(RUN_DIR)/ui.log 2>/dev/null || true; \
	  exit 1; \
	fi
	@echo ""
	@echo "OK: stack running"
	@echo "  Frontend  http://127.0.0.1:$(UI_PORT)"
	@echo "  API/docs  http://127.0.0.1:$(API_PORT)/docs"
	@echo "  Supabase  http://127.0.0.1:54323"
	@echo "  Logs      $(RUN_DIR)/api.log  $(RUN_DIR)/ui.log"
	@echo "  Stop      make -C app stop"

# ---------------------------------------------------------------------------
# stop — app + infra, verify ports
# ---------------------------------------------------------------------------

stop:
	@echo "==> Stopping application ..."
	@if [ -f $(RUN_DIR)/api.pid ]; then \
	  pid=$$(cat $(RUN_DIR)/api.pid); \
	  kill $$pid 2>/dev/null || true; \
	  pkill -P $$pid 2>/dev/null || true; \
	  rm -f $(RUN_DIR)/api.pid; \
	fi
	@if [ -f $(RUN_DIR)/ui.pid ]; then \
	  pid=$$(cat $(RUN_DIR)/ui.pid); \
	  kill $$pid 2>/dev/null || true; \
	  pkill -P $$pid 2>/dev/null || true; \
	  rm -f $(RUN_DIR)/ui.pid; \
	fi
	@for port in $(APP_PORTS); do \
	  if $(MAKE) -f $(firstword $(MAKEFILE_LIST)) _port-busy PORT=$$port >/dev/null 2>&1; then \
	    echo "    freeing port $$port ..."; \
	    fuser -k $$port/tcp 2>/dev/null || lsof -ti:$$port | xargs -r kill -9 2>/dev/null || true; \
	  fi; \
	done
	@echo "==> Stopping Supabase ..."
	@SUPABASE_BIN=$$(command -v supabase 2>/dev/null || echo "$$HOME/.local/bin/supabase"); \
	  if [ -x "$$SUPABASE_BIN" ]; then \
	    cd $(SUPABASE_DIR) && $$SUPABASE_BIN stop 2>/dev/null || true; \
	  fi
	@for port in $(SUPABASE_PORTS); do \
	  if $(MAKE) -f $(firstword $(MAKEFILE_LIST)) _port-busy PORT=$$port >/dev/null 2>&1; then \
	    echo "    freeing port $$port ..."; \
	    fuser -k $$port/tcp 2>/dev/null || lsof -ti:$$port | xargs -r kill -9 2>/dev/null || true; \
	  fi; \
	done
	@echo "==> Verifying ports ..."
	@fail=0; for port in $(ALL_PORTS); do \
	  if $(MAKE) -f $(firstword $(MAKEFILE_LIST)) _port-busy PORT=$$port >/dev/null 2>&1; then \
	    echo "FAIL: port $$port still in use"; fail=1; \
	  else \
	    echo "OK:   port $$port free"; \
	  fi; \
	done; \
	if [ "$$fail" = "1" ]; then \
	  echo "ERROR: some ports still busy — run: ss -tlnp"; \
	  exit 1; \
	fi
	@echo "OK: stop complete"

_port-busy:
	@ss -tln 2>/dev/null | grep -q ":$(PORT) " && exit 0 || exit 1

# ---------------------------------------------------------------------------
# dev / QA helpers
# ---------------------------------------------------------------------------

test:
	@cd $(ROOT) && PYTHONPATH=$(BACKEND_SRC) $(VENV_PY) -m pytest app/backend/tests/ app/shared/tests/ -q
	@cd $(FRONTEND) && npm test

build:
	@cd $(FRONTEND) && npm run build

contracts:
	@cd $(ROOT) && PYTHONPATH=. $(VENV_PY) app/shared/contracts/validate_contracts.py

e2e: build
	@cd $(FRONTEND) && npm run preview -- --host 127.0.0.1 --port $(UI_PORT) & \
	  PREVIEW_PID=$$!; trap 'kill $$PREVIEW_PID 2>/dev/null' EXIT INT TERM; \
	  for _ in $$(seq 1 30); do curl -sf "http://127.0.0.1:$(UI_PORT)/" >/dev/null && break; sleep 0.5; done; \
	  cd $(E2E_DIR) && npm ci --silent 2>/dev/null || npm install; \
	  PLATFORM_UI_URL="http://127.0.0.1:$(UI_PORT)" npm run test:platform
