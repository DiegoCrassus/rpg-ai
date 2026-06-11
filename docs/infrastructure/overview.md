# Infrastructure Overview

## Current Status

**Phase:** Initialization — no deployed services.

Infrastructure will be implemented in `app/infra/` when services are defined.

## Environments

| Environment | Status        | Location           | Notes                              |
|-------------|---------------|--------------------|------------------------------------|
| local       | active        | Developer machine  | SQLite, no containers              |
| dev         | not_ready     | TBD                | Will be defined when services exist|
| staging     | not_ready     | TBD                | TBD                                |
| production  | not_ready     | TBD                | Supabase as database target        |

## Local Stack

```
Developer machine
├── Python virtual environment (pyproject.toml)
├── SQLite database (./data/rpg_op.db)
└── Cursor IDE with MCP servers
```

## Planned Production Stack (TBD)

- **Database:** TBD
- **Backend:** Python service (framework TBD)
- **Frontend:** TBD
- **Container:** Docker (when services are defined)
- **Orchestration:** TBD (Kubernetes or serverless)
- **CI/CD:** GitHub Actions (when pipeline is defined)

## Infrastructure Principles

1. Infrastructure as code — all infrastructure defined in `app/infra/`.
2. No manual console changes — everything versioned and reviewable.
3. Environment parity — local and production use the same configuration format.
4. Rollback first — every deployment has a documented rollback procedure.
