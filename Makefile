.PHONY: sdlc-doctor sdlc-validate sdlc-stages sdlc-sync-model docs-check obs-init obs-server obs-seed sdlc-audit board-in-progress plane-in-progress auto-merge-pr issue-triage board-reformat plane-reformat board-evidence plane-evidence workflow-status workflow-start workflow-discover sdlc-compact-memory sdlc-session-status sdlc-meta-start sdlc-meta-commit sdlc-meta-qa token-budget-status token-budget-reset execution-ledger-status execution-ledger-tail execution-analyze learning-loop-status learning-loop-analyze studio-install studio-dev studio-api studio-smoke studio-e2e supabase-start supabase-stop contracts-validate help

SUPABASE_DIR := app/infra/supabase

help:
	@echo "SDLC AI — Available targets:"
	@echo ""
	@echo "  sdlc-doctor    Run the SDLC Doctor (validates structure, YAML, docs)"
	@echo "  sdlc-validate  Validate YAML schema consistency"
	@echo "  sdlc-sync-model  Compare lifecycle-model write_policy vs paths.yaml shim"
	@echo "  sdlc-stages    List lifecycle stages"
	@echo "  docs-check     Check that all required docs exist and are non-empty"
	@echo ""
	@echo "  obs-init       Initialize SDLC observability database"
	@echo "  obs-server     Start SDLC observability dashboard (http://localhost:7700)"
	@echo "  obs-seed       Insert sample data for dashboard preview"
	@echo ""
	@echo "  sdlc-audit     Run autonomous SDLC audit — generates canvas report"
	@echo "  board-in-progress  Move board card to In Progress (CARD=RPG-N)"
	@echo "  auto-merge-pr  Autonomous squash merge when CI green (PR=N CARD=RPG-N)"
	@echo "  issue-triage   Close superseded repository issues (TRIAGE=1 to apply)"
	@echo "  board-reformat Reformat board card descriptions (CARD=RPG-N or ALL=1)"
	@echo "  board-evidence Post structured Done evidence (CARD=RPG-N)"
	@echo "  workflow-status  Show SDLC session gate + handoff"
	@echo "  workflow-start   Open gate (CARD=RPG-N SLUG=... STAGE=sdlc_meta|implementation)"
	@echo "  workflow-discover  Refresh discovery context from repo + board"
	@echo ""
	@echo "  sdlc-compact-memory  Compact operational-context.md (rolling summary)"
	@echo "  sdlc-session-status  Show session gate status with last_agent + last_commit"
	@echo ""
	@echo "  sdlc-meta-start   Meta-tool: validate + gate + branch (CARD=RPG-N SLUG=...)"
	@echo "  sdlc-meta-commit  Meta-tool: lint + commit + push (CARD=RPG-N MSG='...')"
	@echo "  sdlc-meta-qa      Meta-tool: tests + doctor + QA evidence (CARD=RPG-N)"
	@echo ""
	@echo "  token-budget-status  Show token ledger (session/turn limits)"
	@echo "  token-budget-reset   Reset token session counters"
	@echo ""
	@echo "  execution-ledger-status  Show execution ledger summary"
	@echo "  execution-ledger-tail    Print last N ledger events (N=20 default)"
	@echo "  learning-loop-status   Show learning event store summary"
	@echo "  learning-loop-analyze  Analyze rewards and policy patterns"
	@echo ""
	@echo "  studio-install    Install Studio Python + frontend deps (run once from WSL)"
	@echo "  studio-dev        Studio API :8100 + UI :5174 (requires make studio-install)"
	@echo "  studio-api        Studio API only on :8100"
	@echo "  studio-smoke      HTTP smoke (API must be running; honors STUDIO_AUTH_TOKEN)"
	@echo "  studio-e2e        Playwright E2E — smoke routes + workflow builder"
	@echo ""
	@echo "  supabase-start    Start local Supabase stack (Docker required)"
	@echo "  supabase-stop     Stop local Supabase stack"
	@echo "  contracts-validate  Validate JSON seeds and contract schemas"
	@echo ""
	@echo "  RPG Platform (app/): make -C app help"
	@echo ""
	@echo "Workflow: .sdlc/process/change-lifecycle.md"

PYTHON ?= $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; elif command -v python3 >/dev/null 2>&1; then echo python3; else echo python; fi)
STUDIO_FRONTEND := studio/frontend
STUDIO_BACKEND_SRC := studio/backend/src

sdlc-doctor:
	@echo "Running SDLC Doctor..."
	@$(PYTHON) .sdlc/dsl/cli.py doctor

sdlc-validate:
	@echo "Running SDLC validation..."
	@$(PYTHON) .sdlc/dsl/cli.py validate

sdlc-sync-model:
	@$(PYTHON) .sdlc/scripts/sdlc_sync_model.py

sdlc-stages:
	@$(PYTHON) .sdlc/dsl/cli.py list-stages

docs-check:
	@echo "Checking docs structure..."
	@$(PYTHON) .sdlc/dsl/cli.py doctor > /dev/null && echo "Docs check passed." || echo "Docs check failed — run make sdlc-doctor for details."

obs-init:
	@echo "Initializing SDLC observability database..."
	@mkdir -p app/infra/sdlc_obs/data
	@$(PYTHON) -c "import sys; sys.path.insert(0,'.'); from app.infra.sdlc_obs.collector import Collector; c=Collector(); print('[obs] database initialized at ' + str(c.db_path))"

obs-server:
	@echo "Starting SDLC observability dashboard..."
	@$(PYTHON) app/infra/sdlc_obs/server.py 7700

obs-seed:
	@echo "Inserting sample data..."
	@$(PYTHON) -c "\
import sys; sys.path.insert(0,'.');\
from app.infra.sdlc_obs.collector import Collector;\
runs = [\
  dict(task_name='[AI][PLAN] Backend API design',stage='requirements',agent='planner',task_tags=['[AI]','[PLAN]'],completion_status='completed',tokens_input=900,tokens_output=600,cost_usd=0.0036,tool_calls_total=3,tool_calls_success=3,doctor_exit_code=0),\
  dict(task_name='[AI][INFRA] Setup obs tool',stage='implementation',agent='devops',task_tags=['[AI]','[INFRA]'],completion_status='completed',tokens_input=1500,tokens_output=1100,cost_usd=0.0072,tool_calls_total=8,tool_calls_success=7,tool_calls_failed=1,tests_passed=5,doctor_exit_code=0),\
];\
col = Collector();\
[col.record(**r) for r in runs];\
print('[obs] sample data inserted')"

sdlc-audit:
	@echo "Running SDLC Audit..."
	@$(PYTHON) app/infra/sdlc_obs/auditor.py

board-in-progress:
	@test -n "$(CARD)" || (echo "Usage: make board-in-progress CARD=RPG-N" && exit 1)
	@$(PYTHON) .sdlc/scripts/plane_state.py in-progress --card $(CARD)

plane-in-progress: board-in-progress

auto-merge-pr:
	@test -n "$(PR)" || (echo "Usage: make auto-merge-pr PR=32 CARD=RPG-N" && exit 1)
	@$(PYTHON) .sdlc/scripts/auto_merge_pr.py --pr $(PR) $(if $(CARD),--card $(CARD) --plane-comment,)

issue-triage:
	@$(PYTHON) .sdlc/scripts/github_issue_triage.py $(if $(TRIAGE),--close-superseded,--dry-run)

board-reformat:
	@if [ "$(ALL)" = "1" ]; then $(PYTHON) .sdlc/scripts/plane_card.py reformat-all; \
	else test -n "$(CARD)" || (echo "Usage: make board-reformat CARD=RPG-N or ALL=1" && exit 1); \
	$(PYTHON) .sdlc/scripts/plane_card.py reformat-description --card $(CARD); fi

plane-reformat: board-reformat

board-evidence:
	@test -n "$(CARD)" || (echo "Usage: make board-evidence CARD=RPG-N" && exit 1)
	@$(PYTHON) .sdlc/scripts/plane_card.py post-evidence --card $(CARD) \
	  --file .sdlc/templates/plane/evidence-$(CARD).json

plane-evidence: board-evidence

workflow-status:
	@$(PYTHON) .sdlc/dsl/cli.py workflow status

workflow-start:
	@test -n "$(CARD)" || (echo "Usage: make workflow-start CARD=RPG-N SLUG=my-feature STAGE=implementation" && exit 1)
	@$(PYTHON) .sdlc/dsl/cli.py workflow start --card $(CARD) --slug $(or $(SLUG),work) --stage $(or $(STAGE),implementation) $(if $(FORCE),--force,)

workflow-discover:
	@$(PYTHON) .sdlc/dsl/cli.py workflow discover

sdlc-compact-memory:
	@echo "Compacting SDLC memory context..."
	@$(PYTHON) .sdlc/scripts/compact_memory.py

sdlc-session-status:
	@$(PYTHON) .sdlc/dsl/cli.py workflow status

sdlc-meta-start:
	@test -n "$(CARD)" || (echo "Usage: make sdlc-meta-start CARD=RPG-N SLUG=my-feature [STAGE=implementation]" && exit 1)
	@bash .sdlc/scripts/meta-tools/validate-and-start.sh --card $(CARD) --slug $(or $(SLUG),work) --stage $(or $(STAGE),implementation)

sdlc-meta-commit:
	@test -n "$(CARD)" || (echo "Usage: make sdlc-meta-commit CARD=RPG-N MSG='Short summary' [PATHS='.']" && exit 1)
	@bash .sdlc/scripts/meta-tools/commit-and-push.sh --card $(CARD) --msg "$(MSG)" $(if $(PATHS),--paths "$(PATHS)",)

sdlc-meta-qa:
	@test -n "$(CARD)" || (echo "Usage: make sdlc-meta-qa CARD=RPG-N [TEST_CMD=pytest]" && exit 1)
	@bash .sdlc/scripts/meta-tools/qa-to-review.sh --card $(CARD) $(if $(TEST_CMD),--test-cmd "$(TEST_CMD)",)

token-budget-status:
	@$(PYTHON) .sdlc/scripts/token_budget_status.py status

token-budget-reset:
	@$(PYTHON) .sdlc/scripts/token_budget_status.py reset

execution-ledger-status:
	@$(PYTHON) .sdlc/scripts/execution_ledger.py status

execution-ledger-tail:
	@$(PYTHON) .sdlc/scripts/execution_ledger.py tail -n $(or $(N),20)

execution-analyze:
	@$(PYTHON) .sdlc/scripts/learning_loop.py analyze --last $(or $(N),100)

learning-loop-status:
	@$(PYTHON) .sdlc/scripts/learning_loop.py status

learning-loop-analyze:
	@$(PYTHON) .sdlc/scripts/learning_loop.py analyze --last $(or $(N),100)

export-pdf:
	@echo "Generating simulation PDF..."
	@$(PYTHON) app/infra/sdlc_obs/export_simulation_pdf.py
	@echo "PDF: simulacao-end-to-end-sdlc.pdf"

studio-install:
	@test -x .venv/bin/python || python3 -m venv .venv
	@.venv/bin/pip install -e ".[dev]"
	@cd $(STUDIO_FRONTEND) && rm -rf node_modules && npm install
	@$(MAKE) obs-init

studio-api:
	@echo "Studio API http://127.0.0.1:8100 (Ctrl+C stops)"
	@STUDIO_REPO_ROOT=$$(pwd) PYTHONPATH=$(STUDIO_BACKEND_SRC):$$PWD $(PYTHON) -m uvicorn studio_service.main:app --reload --host 127.0.0.1 --port 8100

studio-smoke:
	@cd $(STUDIO_FRONTEND) && npm run smoke

studio-e2e:
	@bash tests/e2e/run-studio-e2e.sh

studio-dev:
	@test -f $(STUDIO_FRONTEND)/node_modules/vite/bin/vite.js || (echo "Run: make studio-install" && exit 1)
	@$(PYTHON) -c "import uvicorn" 2>/dev/null || (echo "Run: make studio-install (missing uvicorn in $(PYTHON))" && exit 1)
	@echo "Starting Studio API http://127.0.0.1:8100 and UI http://127.0.0.1:5174 (Ctrl+C stops both)"
	@trap 'kill 0' INT TERM EXIT; \
	  STUDIO_REPO_ROOT=$$(pwd) PYTHONPATH=$(STUDIO_BACKEND_SRC):$$PWD $(PYTHON) -m uvicorn studio_service.main:app --reload --host 127.0.0.1 --port 8100 & \
	  cd $(STUDIO_FRONTEND) && npm run dev & \
	  wait

supabase-start:
	@echo "Starting Supabase (config: $(SUPABASE_DIR))..."
	@cd $(SUPABASE_DIR) && supabase start

supabase-stop:
	@echo "Stopping Supabase..."
	@cd $(SUPABASE_DIR) && supabase stop

contracts-validate:
	@echo "Validating shared JSON contracts..."
	@PYTHONPATH=. $(PYTHON) app/shared/contracts/validate_contracts.py
