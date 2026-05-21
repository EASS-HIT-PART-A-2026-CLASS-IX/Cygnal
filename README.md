# 🛡️ Cygnal — Cyber Threat Intelligence Platform

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com)
[![uv](https://img.shields.io/badge/Package_Manager-uv-black)](https://github.com/astral-sh/uv)

Cygnal is a centralized threat intelligence platform for tracking and managing cyber Indicators of Compromise (IOCs).
Built as part of the **EASS-HIT 2026** course — it gives security analysts a single place to ingest, enrich, and act on malicious IPs, domains, URLs, file hashes, and email addresses.

---

## Key Features

- Full CRUD for threat indicators across 5 types: IP, Domain, URL, Hash, Email
- Confidence scoring (0–100) per indicator
- Tagging system with free-form labels (e.g. `ransomware`, `APT29`, `phishing`)
- Threat actor attribution per indicator
- Creation timestamp tracking
- Streamlit dashboard with Plotly charts, filters, free-text search, and CSV export
- JWT authentication with role-based access control (`analyst` / `admin`)
- AI-powered threat analysis via Claude API microservice
- Background worker for automatic IOC ingestion from AbuseIPDB with Redis idempotency
- Automated test suite with isolated in-memory SQLite per test
- Full Docker Compose stack for local multi-service orchestration

---

## Services

| Service | Technology | Port | Role |
|---------|-----------|------|------|
| `api` | FastAPI + SQLModel | 8000 | Core backend, CRUD for IOCs |
| `dashboard` | Streamlit | 8501 | Visual interface for analysts |
| `ai_analyst` | FastAPI + Claude API | 8001 | AI-powered threat analysis |
| `worker` | Python + httpx | — | Auto-imports IOCs from AbuseIPDB |
| `redis` | Redis 7 Alpine | 6379 | Idempotency tracking |

---

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | — | Health check |
| `POST` | `/auth/login` | — | Get JWT token |
| `GET` | `/auth/me` | JWT | Current user info |
| `GET` | `/indicators` | — | List all indicators |
| `POST` | `/indicators` | — | Create a new indicator |
| `GET` | `/indicators/{id}` | — | Get indicator by ID |
| `PUT` | `/indicators/{id}` | — | Update indicator |
| `DELETE` | `/indicators/{id}` | JWT | Delete indicator |
| `POST` | `/indicators/{id}/deactivate` | JWT (admin) | Deactivate indicator |

---

## Project Structure

```
Cygnal/
├── backend/
│   ├── __init__.py
│   ├── auth.py               # JWT + bcrypt authentication
│   ├── config.py             # Environment settings
│   ├── database.py           # SQLite + SQLModel engine
│   ├── models.py             # SQLModel schemas
│   ├── repository.py         # Database operations
│   └── main.py               # FastAPI routes
├── frontend/
│   ├── __init__.py
│   ├── client.py             # Typed HTTP client (httpx)
│   └── dashboard.py          # Streamlit dashboard
├── ai_analyst/
│   ├── __init__.py
│   └── main.py               # Claude API microservice
├── scripts/
│   ├── __init__.py
│   ├── refresh.py            # AbuseIPDB worker with Redis idempotency
│   └── demo.sh               # Local demo walkthrough
├── docs/
│   ├── runbooks/
│   │   └── compose.md        # Docker Compose runbook
│   └── EX3-notes.md          # Architecture decisions + security notes
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures with in-memory SQLite
│   ├── test_main.py          # Backend API tests (16 tests)
│   └── test_frontend.py      # Frontend client tests
├── .env.example
├── Dockerfile
├── compose.yaml
├── examples.http
├── seed.py
├── pyproject.toml
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Validation | Pydantic v2 + SQLModel |
| Storage | SQLite |
| Frontend | Streamlit + Plotly |
| HTTP Client | httpx |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| AI | Claude API (Anthropic) |
| Cache/Queue | Redis 7 |
| Package Manager | uv |
| Testing | pytest + TestClient + anyio |
| Container | Docker + Docker Compose |

---

## Getting Started

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Sync the environment

```bash
uv sync
```

### 3. Copy environment file

```bash
cp .env.example .env
```

### 4. Run the API

```bash
uv run uvicorn backend.main:app --reload
```

API available at `http://127.0.0.1:8000`
Swagger docs at `http://127.0.0.1:8000/docs`

### 5. Seed sample data (optional)

```bash
uv run python seed.py
```

---

## Running API + Dashboard Together

**Terminal 1 — API:**
```bash
uv run uvicorn backend.main:app --reload
```

**Terminal 2 — Streamlit dashboard:**
```bash
uv run streamlit run frontend/dashboard.py
```

- API docs: `http://127.0.0.1:8000/docs`
- Dashboard: `http://localhost:8501`

---

## Running with Docker Compose

```bash
docker compose up --build
```

See `docs/runbooks/compose.md` for full instructions.

---

## Authentication

Login to get a JWT token:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=analyst&password=analyst123"
```

Use the token on protected routes:

```bash
curl -X DELETE http://127.0.0.1:8000/indicators/1 \
  -H "Authorization: Bearer <token>"
```

Default users:

| Username | Password | Role |
|----------|----------|------|
| `analyst` | `analyst123` | analyst |
| `admin` | `admin123` | admin |

---

## Demo

Run the full local demo:

```bash
bash scripts/demo.sh
```

---

## Running Tests

```bash
uv run pytest
```

---

## AI Assistance

This project was developed with the assistance of **Claude (Anthropic)**.
AI tools were used for:

- Designing the project structure and data models
- Implementing SQLModel schemas with SQLite persistence
- Building the Streamlit dashboard with Plotly charts, free-text search, severity-colored rows, and an Edit tab
- Implementing JWT authentication with bcrypt password hashing and role-based access control
- Writing the pytest suite including JWT expiry tests and async anyio tests
- Building the AI analyst microservice with Claude API integration
- Generating and reviewing technical documentation

All AI-generated code was reviewed, understood, and verified locally before being committed.

---

*Created by Agneta Gavrielov — EASS-HIT 2026, Engineering of Advanced Software Solutions*