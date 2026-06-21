# Cygnal Threat Intelligence Platform

Cygnal is a local cyber threat intelligence platform for collecting, validating,
searching, enriching, and reporting Indicators of Compromise (IOCs). It combines
a FastAPI backend, SQLModel persistence, a professional Streamlit analyst
workspace, an asynchronous ingestion worker, Redis, and a free enrichment
microservice.

Built for the EASS-HIT 2026 EX1-EX3 sequence, Cygnal keeps lecturer-facing
commands simple while demonstrating a maintainable multi-service architecture.

## Main Features

- Validated CRUD for IP, domain, URL, hash, and email indicators
- Analyst threat feed with severity styling, search, filters, metrics, and actions
- Dedicated IOC intake with type-specific validation and visual feedback
- Free deterministic enrichment with risk score, evidence, history, and actions
- Optional local Ollama explanation; no paid API or key is required
- JWT authentication, role checks, rate limits, trace IDs, ETags, and CSV export
- Async worker with retries, bounded concurrency, and Redis idempotency
- Docker Compose orchestration and automated quality/release gates

## Architecture

| Service | Technology | Purpose |
| --- | --- | --- |
| `api` | FastAPI, SQLModel, SQLite | IOC validation, CRUD, auth, exports, contracts |
| `dashboard` | Streamlit, Plotly | User-facing analyst workspace |
| `worker` | asyncio, httpx | Mock or AbuseIPDB IOC ingestion |
| `ai_analyst` | FastAPI | Free structured IOC scoring and optional Ollama narrative |
| `redis` | Redis 7 | Rate limiting and worker idempotency |

The backend remains the source of truth. The dashboard and enrichment service
communicate with it through documented HTTP contracts.

## Monorepo Structure

```text
.
|-- backend/          FastAPI routes, schemas, models, repositories, and services
|-- frontend/         Streamlit pages, components, API client, state, and styling
|-- ai_analyst/       Free deterministic enrichment service and optional Ollama client
|-- worker/           Async refresh and Redis idempotency implementation
|-- tests/            Backend, frontend, worker, and enrichment tests
|-- scripts/          Seed, demo, refresh, release, and FastMCP utilities
|-- docs/             Product spec, EX3 evidence, contracts, checklist, and runbooks
|-- .github/          GitHub Actions workflow
|-- compose.yaml      Local multi-service orchestration
|-- Dockerfile        Shared Python service image
|-- examples.http     Lecturer-friendly REST request playground
`-- pyproject.toml    Python dependencies and tool configuration
```

## Run Locally

Requirements: Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env
uv run uvicorn backend.main:app --reload
```

In separate terminals:

```bash
uv run streamlit run frontend/dashboard.py
uv run uvicorn ai_analyst.main:app --port 8001
uv run python scripts/refresh.py
```

| Surface | URL |
| --- | --- |
| Dashboard | http://localhost:8501 |
| API/OpenAPI | http://localhost:8000/docs |
| Enrichment API | http://localhost:8001/docs |

Demo accounts are local classroom fixtures:

| Username | Password | Role |
| --- | --- | --- |
| `analyst` | `analyst123` | Analyst |
| `admin` | `admin123` | Administrator |

Set a strong `JWT_SECRET_KEY` before any non-classroom use.

## Run with Docker Compose

```bash
docker compose up --build
```

Compose starts the API, dashboard, enrichment service, worker, and Redis. See
[the Compose runbook](docs/runbooks/compose.md) for health and demo commands.

## Free Enrichment Mode

The default engine works without network access or API keys. It combines
severity, confidence, active state, relevant tags, IOC type, source context, and
database history into a structured result containing:

- risk score and level;
- analysis confidence and reasoning;
- IOC-type and source analysis;
- first-seen/history information;
- recommended analyst actions.

Ollama is optional. To add a local-model explanation:

```bash
ollama pull llama3.2:3b
# Local uv run:
export OLLAMA_BASE_URL=http://localhost:11434
# Compose on Docker Desktop:
export OLLAMA_BASE_URL=http://host.docker.internal:11434
```

If Ollama is unavailable, Cygnal automatically returns the complete deterministic
assessment. The local model never replaces or changes the authoritative score.

## Tests and CI/CD

```bash
uv run pytest
uvx ruff format --check .
uvx ruff check .
uvx --from mypy==1.19.1 mypy backend frontend ai_analyst worker scripts
uv run python scripts/check_release.py
```

GitHub Actions runs formatting, linting, typing, pytest with coverage,
Schemathesis contract tests, MkDocs, pdoc, and a FastMCP probe.

## Course Coverage

- **EX1:** FastAPI CRUD, Pydantic validation, SQLite, pytest, README, seed script,
  and `.http` playground
- **EX2:** Streamlit list/create workflows, guidance, search, edit/delete, charts,
  CSV export, and automated interface checks
- **EX3:** five-service Compose stack, async retries/concurrency, Redis
  idempotency, JWT role checks, free enrichment, CI, contracts, runbooks, and demo
  automation

Detailed evidence is in [EX3 notes](docs/EX3-notes.md) and the
[course-alignment checklist](docs/course-alignment.md).

## AI Assistance Disclosure

Claude and OpenAI Codex assisted with design review, implementation, testing, and
documentation. Generated changes were reviewed and verified with automated tests
and live Compose checks. Cygnal runtime functionality does not require a paid AI
service.
