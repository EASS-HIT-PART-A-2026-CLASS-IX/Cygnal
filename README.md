# Cygnal Threat Intelligence Platform

Cygnal is a local cyber threat intelligence platform for collecting, validating,
searching, enriching, and reporting Indicators of Compromise (IOCs). It combines
a FastAPI backend, SQLModel persistence, a professional Streamlit analyst
workspace, an asynchronous ingestion worker, Redis, and a free enrichment
microservice.

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
| `worker` | asyncio, httpx | AbuseIPDB ingestion with an offline fallback dataset |
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

Run the dashboard and enrichment API in separate terminals:

```bash
uv run streamlit run frontend/dashboard.py
uv run uvicorn ai_analyst.main:app --port 8001
```

After the API is healthy, load the demonstration dataset once:

```bash
uv run python scripts/seed.py
```

Local worker refresh requires Redis. Start Redis, then run one refresh:

```bash
docker compose up -d redis
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

Compose starts the API, dashboard, enrichment service, worker, and Redis. The worker
idempotently loads ten safe, varied demonstration IOCs before its scheduled IP
refresh, and SQLite data persists in a named Docker volume. See
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

Ollama is optional and affects only `POST /analyze` on the `ai_analyst`
service. Without Ollama, analysis remains fully offline with
`analysis_mode: "deterministic"` and `local_model_explanation: null`. When
enabled, the deterministic score and recommendations remain authoritative;
Ollama only adds a local narrative explanation, returning
`analysis_mode: "deterministic+ollama"` and a populated
`local_model_explanation`.

| Variable | Purpose | Default |
| --- | --- | --- |
| `OLLAMA_BASE_URL` | Enables Ollama and selects its endpoint | Empty (disabled) |
| `OLLAMA_MODEL` | Local model used for the explanation | `llama3.2:3b` |
| `OLLAMA_TIMEOUT_SECONDS` | Maximum Ollama request time | `5` |

Ollama must run separately on the host; Docker Compose does not start it.

```bash
# Unix: local Python
ollama pull llama3.2:3b
export OLLAMA_BASE_URL=http://localhost:11434

# Unix: Docker Desktop
export OLLAMA_BASE_URL=http://host.docker.internal:11434
docker compose up --build -d ai_analyst
```

```powershell
# Windows PowerShell: local Python
ollama pull llama3.2:3b
$env:OLLAMA_BASE_URL="http://localhost:11434"

# Windows PowerShell: Docker Desktop
$env:OLLAMA_BASE_URL="http://host.docker.internal:11434"
docker compose up --build -d ai_analyst
```

With the backend and enrichment service running, verify an existing indicator:

```powershell
$result = Invoke-RestMethod -Method Post -Uri http://localhost:8001/analyze `
  -ContentType application/json -Body '{"indicator_id":1}'
$result.analysis_mode  # expected: deterministic+ollama
```

## Scope and Limitations

- SQLite persistence and fixture credentials are intended for local academic and
  demonstration use.
- The dashboard currently retrieves the first 100 indicators from the API.
- Ollama and AbuseIPDB are optional; deterministic enrichment and offline worker
  fallback data remain available without them.

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
