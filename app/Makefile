# RPG Platform — local development shortcuts
#
# Run from repo root:  make -C app help
# Or from this dir:    make help

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
BACKEND_SRC := $(ROOT)/app/backend/src
FRONTEND := $(ROOT)/app/frontend
SUPABASE_DIR := $(ROOT)/app/infra/supabase
E2E_DIR := $(ROOT)/tests/e2e

API_PORT ?= 8000
UI_PORT ?= 5173

PYTHON ?= $(shell if [ -x $(ROOT)/.venv/bin/python ]; then echo $(ROOT)/.venv/bin/python; elif command -v python3 >/dev/null 2>&1; then echo python3; else echo python; fi)

.PHONY: help install test backend-test frontend-test shared-test build api dev \
        contracts supabase-start supabase-stop supabase-reset e2e smoke

help:
	@echo "RPG Platform (app/)"
	@echo ""
	@echo "  make install          Python venv + backend deps + frontend npm"
	@echo "  make dev              API :$(API_PORT) + UI :$(UI_PORT) (requires install)"
	@echo "  make api              FastAPI only on :$(API_PORT)"
	@echo "  make test             backend + shared + frontend tests"
	@echo "  make backend-test     pytest app/backend/tests"
	@echo "  make frontend-test    vitest (app/frontend)"
	@echo "  make shared-test      pytest app/shared/tests"
	@echo "  make build            production build (frontend)"
	@echo "  make contracts        validate JSON schemas + seeds"
	@echo "  make e2e              Playwright platform smoke (UI preview)"
	@echo "  make smoke            HTTP health check (API must be running)"
	@echo ""
	@echo "  make supabase-start   Start local Supabase (Docker + CLI)"
	@echo "  make supabase-stop    Stop local Supabase"
	@echo "  make supabase-reset   Reset DB + re-apply migrations"
	@echo ""
	@echo "Prerequisites: copy $(ROOT)/.env.example → .env and $(FRONTEND)/.env.example → $(FRONTEND)/.env"
	@echo "Full stack: make supabase-start && make dev"

install:
	@test -x $(ROOT)/.venv/bin/python || $(PYTHON) -m venv $(ROOT)/.venv
	@$(ROOT)/.venv/bin/pip install -e "$(ROOT)[dev,agent]"
	@cd $(FRONTEND) && npm install
	@echo "OK: RPG Platform dependencies installed"

backend-test:
	@cd $(ROOT) && PYTHONPATH=$(BACKEND_SRC) $(ROOT)/.venv/bin/python -m pytest app/backend/tests/ -q

shared-test:
	@cd $(ROOT) && $(ROOT)/.venv/bin/python -m pytest app/shared/tests/ -q

frontend-test:
	@cd $(FRONTEND) && npm test

test: backend-test shared-test frontend-test

build:
	@cd $(FRONTEND) && npm run build

api:
	@echo "RPG Platform API http://127.0.0.1:$(API_PORT) (Ctrl+C stops)"
	@cd $(ROOT) && PYTHONPATH=$(BACKEND_SRC) $(ROOT)/.venv/bin/python -m uvicorn rpg_platform.main:app \
		--reload --host 127.0.0.1 --port $(API_PORT)

dev:
	@test -f $(FRONTEND)/node_modules/vite/bin/vite.js || (echo "Run: make install" && exit 1)
	@test -x $(ROOT)/.venv/bin/python || (echo "Run: make install" && exit 1)
	@echo "Starting RPG API http://127.0.0.1:$(API_PORT) and UI http://127.0.0.1:$(UI_PORT) (Ctrl+C stops both)"
	@trap 'kill 0' INT TERM EXIT; \
	  cd $(ROOT) && PYTHONPATH=$(BACKEND_SRC) $(ROOT)/.venv/bin/python -m uvicorn rpg_platform.main:app \
	    --reload --host 127.0.0.1 --port $(API_PORT) & \
	  cd $(FRONTEND) && npm run dev -- --port $(UI_PORT) & \
	  wait

contracts:
	@cd $(ROOT) && PYTHONPATH=. $(ROOT)/.venv/bin/python app/shared/contracts/validate_contracts.py

smoke:
	@curl -sf "http://127.0.0.1:$(API_PORT)/api/v1/health" >/dev/null \
	  && echo "OK: API health" \
	  || (echo "FAIL: API not reachable on :$(API_PORT) — run make api or make dev" && exit 1)

e2e:
	@cd $(FRONTEND) && npm run build
	@cd $(FRONTEND) && npm run preview -- --port $(UI_PORT) & \
	  PREVIEW_PID=$$!; \
	  trap 'kill $$PREVIEW_PID 2>/dev/null' EXIT INT TERM; \
	  for _ in $$(seq 1 30); do curl -sf "http://127.0.0.1:$(UI_PORT)/" >/dev/null && break; sleep 0.5; done; \
	  cd $(E2E_DIR) && npm ci --silent 2>/dev/null || npm install; \
	  PLATFORM_UI_URL="http://127.0.0.1:$(UI_PORT)" npm run test:platform

supabase-start:
	@echo "Starting Supabase (config: $(SUPABASE_DIR))..."
	@cd $(SUPABASE_DIR) && supabase start

supabase-stop:
	@echo "Stopping Supabase..."
	@cd $(SUPABASE_DIR) && supabase stop

supabase-reset:
	@echo "Resetting Supabase database..."
	@cd $(SUPABASE_DIR) && supabase db reset
