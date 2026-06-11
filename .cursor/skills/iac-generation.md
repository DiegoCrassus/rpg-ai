# Skill: IaC Generation

## Purpose

Generate reproducible Terraform modules for stack services (PostgreSQL, Redis, backend, frontend) from architecture definition in `docs/architecture/`, ensuring infrastructure is provisioned deterministically without human intervention.

## When to use

- After Architect finalizes `docs/architecture/overview.md` and ADRs
- When Implementer needs staging or production environment for integration tests
- As Deployment stage gate: IaC must exist and be valid before deploy

## Required inputs

- `docs/architecture/overview.md` — defines services and configurations
- `docs/architecture/decisions.md` — ADRs with infrastructure decisions
- `.sdlc/memory/architecture.md` — infrastructure constraints
- Environment variables: `TF_VAR_*` for credentials and configuration

## Procedure

### 1. Generate base structure

```
app/infra/terraform/
├── main.tf            ← provider config + workspace
├── variables.tf       ← all configurable variables
├── outputs.tf         ← outputs for other modules
├── modules/
│   ├── database/      ← PostgreSQL (RDS / Cloud SQL / local)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── cache/         ← Redis (ElastiCache / Azure Cache / local)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── backend/       ← Container service (ECS / Cloud Run / Docker)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── frontend/      ← CDN / static hosting (CloudFront / Vercel / nginx)
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/
    ├── local.tfvars   ← variables for local Docker Compose
    └── staging.tfvars ← variables for staging environment
```

### 2. Validate generated IaC

```bash
cd app/infra/terraform
terraform init -backend=false
terraform validate
terraform fmt -check

# For local environment with Docker
terraform plan -var-file=environments/local.tfvars -out=plan.tfplan
```

### 3. Database module template (PostgreSQL)

```hcl
# app/infra/terraform/modules/database/main.tf
variable "db_name"     { type = string }
variable "db_user"     { type = string }
variable "db_password" { type = string; sensitive = true }
variable "db_port"     { type = number; default = 5432 }
variable "environment" { type = string; default = "local" }

resource "docker_container" "postgres" {
  count = var.environment == "local" ? 1 : 0
  name  = "postgres-${var.environment}"
  image = "postgres:16-alpine"
  env = [
    "POSTGRES_DB=${var.db_name}",
    "POSTGRES_USER=${var.db_user}",
    "POSTGRES_PASSWORD=${var.db_password}",
  ]
  ports { internal = 5432; external = var.db_port }
}

output "connection_string" {
  value     = "postgresql://${var.db_user}:${var.db_password}@localhost:${var.db_port}/${var.db_name}"
  sensitive = true
}
```

### 4. Cache module template (Redis)

```hcl
# app/infra/terraform/modules/cache/main.tf
variable "redis_port"  { type = number; default = 6379 }
variable "environment" { type = string; default = "local" }

resource "docker_container" "redis" {
  count = var.environment == "local" ? 1 : 0
  name  = "redis-${var.environment}"
  image = "redis:7-alpine"
  command = ["redis-server", "--save", "", "--loglevel", "warning"]
  ports { internal = 6379; external = var.redis_port }
}

output "redis_url" {
  value = "redis://localhost:${var.redis_port}"
}
```

## Outputs

- `app/infra/terraform/` with all modules generated
- `terraform validate` passes without errors
- `terraform plan` produces plan without syntax errors
- Outputs documented in `outputs.tf` for backend consumption

## Validation checklist

- [ ] `terraform init -backend=false` without errors
- [ ] `terraform validate` passes
- [ ] `terraform fmt -check` with no differences (formatted code)
- [ ] No hardcoded credentials — all in `variables.tf` with `sensitive = true`
- [ ] `environments/local.tfvars` exists and provides all required values
- [ ] Outputs include connection strings for database and cache

## Failure modes

| Failure | Cause | Action |
|-------|-------|------|
| `terraform validate` fails | Syntax error in HCL | Fix per validate output |
| Provider not found | `terraform init` not run | Run `terraform init -backend=false` first |
| Sensitive variable exposed | Hardcoded in code | Move to `variables.tf` with `sensitive = true` |
| Module not found | Incorrect `source` path | Verify directory structure |
