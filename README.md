# Cygnal Threat Intelligence Platform

Cygnal is a local full-stack cybersecurity platform for collecting, searching,
analyzing, and reporting Indicators of Compromise (IOCs). It combines a FastAPI
backend, SQLModel persistence, an authenticated Streamlit workspace, an async
ingestion worker, Redis, and an optional Claude-powered analysis service.

Built for the EASS-HIT 2026 EX1-EX3 sequence, Cygnal keeps the required
course-facing commands simple while demonstrating a maintainable microservice
architecture.

## Highlights

- Validated CRUD API for IPs, domains, URLs, hashes, and email indicators
- Dedicated login flow and role-aware JWT authorization
- Multi-page analyst workspace with Dark, Light, and System themes
- Search, server-side filters, charts, CSV export, and AI-generated reports
- Paginated API contract with ETag, trace IDs, and Redis-backed rate limits
- Async worker with retries, bounded concurrency, and Redis idempotency
- Docker Compose orchestration and automated release gates
- 43 automated backend, frontend, worker, and AI service tests

## Architecture

| Component | Technology | Purpose |
|---|---|---|
| `api` | FastAPI, SQLModel, SQLite | IOC contracts, CRUD, authentication, exports |
| `dashboard` | Streamlit, Plotly | Authenticated analyst workspace |
| `worker` | asyncio, httpx | IOC ingestion from AbuseIPDB or deterministic mock data |
| `ai_analyst` | FastAPI, Anthropic API | IOC assessments and summary reports |
| `redis` | Redis 7 | Rate limiting and worker idempotency |

The main entrypoints are intentionally stable:

- API: `backend/main.py`
- Dashboard: `frontend/dashboard.py`
- Worker: `scripts/refresh.py`
- AI Analyst: `ai_analyst/main.py`

Implementation details are separated into routes, schemas, models, repositories,
services, UI views, reusable components, and service-specific packages.

## Quick Start

Requirements: Python 3.12, [uv](https://docs.astral.sh/uv/), and Docker Desktop
for the complete stack.

```bash
uv sync
cp .env.example .env
uv run python scripts/seed.py
```

Run the API and dashboard locally in separate terminals:

```bash
uv run uvicorn backend.main:app --reload
uv run streamlit run frontend/dashboard.py
```

Or start the complete system:

```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Dashboard | `http://localhost:8501` |
| API documentation | `http://localhost:8000/docs` |
| AI Analyst documentation | `http://localhost:8001/docs` |

Demo-only users:

| Username | Password | Role |
|---|---|---|
| `analyst` | `analyst123` | Analyst |
| `admin` | `admin123` | Administrator |

These credentials and the fallback JWT secret are for local demonstration only.
Configure `JWT_SECRET_KEY` before using Cygnal outside a local classroom setup.

## Core API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health, trace, and rate-limit probe |
| `POST` | `/auth/login` | Issue a JWT |
| `GET` | `/auth/me` | Validate the current JWT |
| `GET` | `/indicators` | List and filter indicators |
| `GET` | `/indicators/page` | Paginated list with ETag |
| `GET` | `/indicators/export.csv` | Filtered CSV export |
| `POST` | `/indicators` | Create an indicator |
| `PUT` | `/indicators/{id}` | Update an indicator |
| `DELETE` | `/indicators/{id}` | Authenticated deletion |
| `POST` | `/indicators/{id}/deactivate` | Admin-only deactivation |

See [examples.http](examples.http) and
[docs/service-contract.md](docs/service-contract.md) for executable examples and
the complete contract.

## Testing And Quality

Run the automated test suite:

```bash
uv run pytest
```

Run the full CI-equivalent release sequence while the Compose API is available:

```bash
uv run python scripts/check_release.py
```

The release sequence covers pytest with coverage, Ruff, mypy, Schemathesis,
MkDocs, pdoc, and the FastMCP contract probe. GitHub Actions runs the same
quality gates on pushes and pull requests.

## Demo And Documentation

Run the grader-oriented walkthrough:

```bash
bash scripts/demo.sh
```

Additional project evidence:

- [EX3 architecture and security notes](docs/EX3-notes.md)
- [Compose runbook](docs/runbooks/compose.md)
- [Release checklist](docs/release-checklist.md)
- [Project specification](spec.md)

Database setup is reproducible through `scripts/seed.py`. SQLite database files,
local environment files, caches, and generated documentation are ignored by Git.

## Course Requirement Coverage

- **EX1:** validated FastAPI CRUD, SQLite persistence, pytest coverage,
  documentation, seed script, and `.http` playground
- **EX2:** Streamlit interface supporting list/create workflows, user guidance,
  filtering, analytics, CSV export, and automated interface testing
- **EX3:** Compose orchestration, async worker reliability, Redis idempotency,
  JWT role checks, AI/reporting enhancements, CI, release documentation, and
  local demo script

## AI Assistance

Claude and OpenAI Codex assisted with architecture review, implementation,
testing, UI refinement, and documentation. Every generated change was reviewed,
understood, and verified locally with automated tests and runtime checks before
submission.
