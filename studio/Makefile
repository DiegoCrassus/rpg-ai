# SDLC Studio — local development shortcuts
#
# Run from repo root for full stack: `make studio-dev`

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)
PYTHON ?= $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null)

.PHONY: help test engine-test backend-test frontend-test cli-compile

help:
	@echo "SDLC Studio (studio/)"
	@echo ""
	@echo "  make test           engine + backend pytest"
	@echo "  make engine-test    Foundation engine tests only"
	@echo "  make backend-test   Studio Service API tests"
	@echo "  make frontend-test  Vitest (studio/frontend)"
	@echo "  make cli-compile    python -m studio.cli compile"
	@echo ""
	@echo "Full stack: make studio-dev (from repo root)"

test: engine-test backend-test

engine-test:
	@cd $(ROOT) && $(PYTHON) -m pytest studio/engine/tests/ -q

backend-test:
	@cd $(ROOT) && STUDIO_REPO_ROOT=$(ROOT) PYTHONPATH=studio/backend/src:$(ROOT) \
		$(PYTHON) -m pytest studio/backend/tests/ -q

frontend-test:
	@cd $(ROOT)/studio/frontend && npm run test

cli-compile:
	@cd $(ROOT) && $(PYTHON) -m studio.cli compile
