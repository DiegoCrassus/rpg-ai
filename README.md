# RPG AI

Plataforma web para gestão de campanhas de RPG de mesa (**RPG Platform**) e sistema operacional SDLC com agentes de IA (**SDLC Studio**).

Cada **Mesa** é um sandbox isolado: o Mestre faz bootstrap enviando uma ficha (PDF/PNG), um agente propõe templates, jogadores recebem convites e editam fichas e documentos com permissões por campanha.

## O que há no repositório

| Área | Caminho | Descrição |
|------|---------|-----------|
| **Produto** | [`app/`](app/) | API FastAPI, SPA React, contratos JSON, Supabase |
| **Especificação** | [`docs/product/`](docs/product/) | Escopo MVP, contratos, schema de banco |
| **Arquitetura** | [`docs/architecture/`](docs/architecture/) | Visão técnica e ADRs |
| **SDLC** | [`.sdlc/`](.sdlc/), [`AGENTS.md`](AGENTS.md) | Workflow, Doctor, CLI |
| **Studio** | [`studio/`](studio/) | Painel de controle SDLC (API + UI) |
| **Cursor** | [`.cursor/`](.cursor/) | Agentes, hooks, skills |

## Stack do produto (`app/`)

| Camada | Tecnologia |
|--------|------------|
| Frontend | React 19 · Vite · TypeScript · Tailwind · Supabase Auth (client) |
| Backend | Python 3.11+ · FastAPI · SQLAlchemy async · PyJWT |
| Dados | Supabase Postgres + Storage (local via CLI ou cloud) |
| Agente | Deep Agent (LangChain) para import de fichas |
| Contratos | JSON Schema em `app/shared/contracts/` |

```
app/
├── backend/src/rpg_platform/   # REST /api/v1
├── frontend/src/               # SPA PT-BR (:5173)
├── shared/
│   ├── contracts/              # *.v1.schema.json
│   ├── seeds/dnd5e/            # fallback D&D 5e
│   └── references/             # glossários para o agente
└── infra/
    ├── supabase/               # migrations, config.toml
    └── sdlc_obs/               # métricas SDLC (ortogonal)
```

## Pré-requisitos

- **Python 3.11+** e **Node.js 20+**
- **Docker Desktop** + [Supabase CLI](https://supabase.com/docs/guides/cli) (stack local)
- Chave **OpenAI** (opcional — só para o Sheet Import Agent)

## Início rápido — RPG Platform

### 1. Variáveis de ambiente

```bash
cp .env.example .env
cp app/frontend/.env.example app/frontend/.env
```

Preencha `.env` com os valores do Supabase (passo 2) e, se for usar import de fichas, `OPENAI_API_KEY`.

### 2. Supabase local

```bash
make -C app supabase-start
```

Copie do output do CLI para `.env`: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`, `DATABASE_URL`.

Copie `SUPABASE_ANON_KEY` para `app/frontend/.env` como `VITE_SUPABASE_ANON_KEY`.

### 3. Dependências e desenvolvimento

```bash
make -C app install
make -C app dev
```

| Serviço | URL |
|---------|-----|
| Frontend | http://127.0.0.1:5173 |
| API + OpenAPI | http://127.0.0.1:8000/docs |
| Supabase Studio | http://127.0.0.1:54323 |

### 4. Testes

```bash
make -C app test              # pytest backend + shared + vitest frontend
make -C app contracts         # valida JSON schemas e seeds
make -C app e2e               # smoke Playwright (rotas auth)
```

Comandos úteis: `make -C app help`.

## Jornadas MVP

Fluxos principais documentados em [`docs/product/mvp-scope.md`](docs/product/mvp-scope.md):

1. **Mestre** — criar mesa → upload de ficha → revisar proposta → mesa ativa  
2. **Mestre** — convidar jogador por e-mail  
3. **Jogador** — aceitar convite → documentos visíveis → criar/editar personagem  

Rotas da SPA: `/login`, `/mesas`, `/mesas/:id/import`, `/mesas/:id/characters`, `/mesas/:id/documents`, `/profile`, `/admin`.

## SDLC e Studio

Este repositório também hospeda o pipeline SDLC com agentes Cursor:

```bash
make sdlc-doctor              # valida estrutura e YAML
make workflow-status          # gate + handoff ativo
make studio-dev               # Studio UI :5174 + API :8100
```

Entrada do orchestrator: [`AGENTS.md`](AGENTS.md) · processo: [`.sdlc/process/change-lifecycle.md`](.sdlc/process/change-lifecycle.md).

## Documentação

| Tópico | Link |
|--------|------|
| Escopo MVP | [`docs/product/mvp-scope.md`](docs/product/mvp-scope.md) |
| Contratos JSON | [`docs/product/json-contracts.md`](docs/product/json-contracts.md) |
| Visão arquitetural | [`docs/architecture/rpg-platform-overview.md`](docs/architecture/rpg-platform-overview.md) |
| Supabase local | [`app/infra/supabase/README.md`](app/infra/supabase/README.md) |
| Import de fichas | [`docs/product/sheet-import-agent.md`](docs/product/sheet-import-agent.md) |

## CI

GitHub Actions (`.github/workflows/ci.yml`): Doctor, pytest, ruff, contratos JSON, secrets scan, Studio E2E e smoke da plataforma.
