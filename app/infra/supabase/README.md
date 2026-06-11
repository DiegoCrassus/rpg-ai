# Supabase — RPG Platform (local)

PostgreSQL control plane + Auth + Storage for the RPG platform MVP.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) running (WSL2 integration enabled)
- [Supabase CLI](https://supabase.com/docs/guides/cli) installed (`>= 1.200`)

### Install CLI (WSL / Linux)

If `supabase: not found`:

```bash
make -C app install-supabase-cli
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
supabase --version
```

## Quick start

From the repository root:

```bash
make -C app migrate  # apply migrations + seed admin (db reset, local)
make -C app infra    # Supabase only
make -C app start    # Supabase + API + frontend
make -C app stop     # stop everything
```

`migrate` runs `supabase db reset` (wipes local DB, reapplies `migrations/*.sql`).

**Dev admin** (from `00002_seed_admin_user.sql`): `admin@rpg.local` / `RpgAdmin!local`

`infra` installs the Supabase CLI to `~/.local/bin` if missing and requires Docker Desktop.

After start, copy connection values into `.env` (see `.env.example`):

| Variable | Source |
|----------|--------|
| `SUPABASE_URL` | CLI output — API URL (default `http://127.0.0.1:54321`) |
| `SUPABASE_ANON_KEY` | CLI output — anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | CLI output — service role key |
| `SUPABASE_JWT_SECRET` | CLI output — JWT secret |
| `DATABASE_URL` | CLI output — Postgres connection string |

Studio UI: http://127.0.0.1:54323

## Migrations

DDL lives in `migrations/00001_rpg_platform_schema.sql` (source of truth: `docs/product/database-schema.md`).

Apply / reset:

```bash
cd app/infra/supabase
supabase db reset
```

## Storage buckets

Created by migration:

| Bucket | Purpose |
|--------|---------|
| `profiles` | User avatars (`{user_id}/avatar.*`) |
| `campaigns` | Campaign tree (`{mesa_id}/…`) |

Both buckets are **private** — clients access files through FastAPI only.

## Stop

```bash
make supabase-stop
```

## Validate JSON contracts (no Docker required)

```bash
make contracts-validate
```
