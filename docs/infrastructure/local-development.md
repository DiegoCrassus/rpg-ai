# Local Development Setup

## Prerequisites

- Python 3.11+ (check: `python --version`)
- pip or uv (for dependency management)
- Git
- Cursor IDE (for AI-native workflow)

## Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/DiegoCrassus/sdlc-ai.git
cd sdlc-ai

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -e ".[dev]"
# or if using uv:
uv sync

# 4. Copy and configure environment
cp .env.example .env  # NOTE: .env.example does not exist yet — TBD
# Edit .env with your credentials

# 5. Validate the repository structure
make sdlc-doctor
```

## Environment Variables

Required variables (see `.env` for full list):

| Variable                              | Purpose                    |
|---------------------------------------|----------------------------|
| `GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC`| GitHub MCP access          |
| `PLANE_API_KEY`                       | Plane task management      |
| `OPENAI_API_KEY`                      | LLM inference              |
| `DATABASE_URL`                        | Local SQLite path          |
| `AGENT_MODEL`                         | LLM model identifier       |

## Running the SDLC Doctor

```bash
make sdlc-doctor
```

Expected output: all `[PASS]`, some `[WARN]` for unconfigured integrations.

## Running the MarketPulse App

The MarketPulse application (FastAPI backend + React/Vite frontend) ships with a
Makefile in `app/` that provides one-command local development. Run all targets
from the `app/` directory. The Makefile was introduced in Plane card **INVES-30**
and merged via [PR #44](https://github.com/DiegoCrassus/sdlc-ai/pull/44).

`make install` and `make start` automatically create and use a project virtual
environment at the repo root (`.venv`) when you run them from `app/`, avoiding
PEP 668 “externally-managed-environment” errors on Debian/Ubuntu system Python.
The manual venv step in Initial Setup above remains a valid alternative.

```bash
cd app
make start
```

`make start` installs dependencies if needed, then runs the backend and frontend
together:

- Backend (FastAPI): http://127.0.0.1:8000 — interactive docs at http://127.0.0.1:8000/docs
- Frontend (Vite): http://127.0.0.1:5173

Press `Ctrl+C` to stop both processes.

### Available targets

| Target              | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `make start`        | Install deps (if needed) and run backend + frontend together                |
| `make install`      | Create `.venv` if needed, install backend + frontend deps                     |
| `make install-backend` | Create `.venv` if needed, install backend deps (editable `.[dev]`)         |
| `make install-frontend` | Install frontend npm dependencies                                        |
| `make venv`         | Create repo-root `.venv` only (no package install)                            |
| `make backend`      | Run only the FastAPI backend (reload mode)                                   |
| `make frontend`     | Run only the Vite frontend dev server                                        |
| `make test`         | Run backend tests (pytest; works on a cold checkout via `PYTHONPATH`)        |
| `make clean`        | Remove caches and build artifacts                                            |
| `make help`         | List all available targets                                                   |

### Configurable variables

Override these on the command line as needed:

| Variable       | Default     | Purpose                          |
|----------------|-------------|----------------------------------|
| `PYTHON`       | `.venv/bin/python` when present, else `python3` | Python interpreter to use |
| `BACKEND_HOST` | `127.0.0.1` | Host the backend binds to        |
| `BACKEND_PORT` | `8000`      | Port the backend listens on      |

```bash
# Example: run the backend on a different port
cd app
make start BACKEND_PORT=8080
```

## Known Local Setup Issues

- Container setup (Docker) will be documented here when container images are defined.

## IDE Configuration

Open the project in Cursor. The `.cursor/` directory will be automatically loaded by Cursor, providing:
- Agent rules
- Command shortcuts
- Skill procedures
- SDLC context
