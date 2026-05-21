# 🛡️ Cygnal — Cyber Threat Intelligence Platform

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com)
[![uv](https://img.shields.io/badge/Package_Manager-uv-black)](https://github.com/astral-sh/uv)

Cygnal is a centralized platform for managing and sharing cyber threat indicators (IOCs).
Built as part of the **EASS-HIT 2026** course, it enables security analysts to track malicious IPs, domains, URLs, file hashes, and email addresses — with confidence scoring, tagging, and threat actor attribution.

---

## Key Features

- Full CRUD for threat indicators across 5 types: IP, Domain, URL, Hash, Email
- Confidence scoring (0–100) per indicator
- Tagging system with free-form labels (e.g. `ransomware`, `APT29`, `phishing`)
- Threat actor attribution per indicator
- Creation timestamp tracking
- Streamlit dashboard with charts, filters, free-text search, and CSV export
- Automated test suite with isolated in-memory SQLite per test
- Docker support for consistent local and container environments

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/indicators` | List all indicators |
| `POST` | `/indicators` | Create a new indicator |
| `GET` | `/indicators/{id}` | Get indicator by ID |
| `PUT` | `/indicators/{id}` | Update indicator |
| `DELETE` | `/indicators/{id}` | Delete indicator |

---

## Project Structure

```
Cygnal/
├── backend/
│   ├── __init__.py
│   ├── config.py             # Environment settings
│   ├── database.py           # SQLite + SQLModel engine
│   ├── models.py             # SQLModel schemas
│   ├── repository.py         # Database operations
│   └── main.py               # FastAPI routes
├── frontend/
│   ├── __init__.py
│   ├── client.py             # Typed HTTP client (httpx)
│   └── dashboard.py          # Streamlit dashboard
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures with in-memory SQLite
│   ├── test_main.py          # Backend API tests
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
| Package Manager | uv |
| Testing | pytest + TestClient |
| Container | Docker |

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

### 3. Run the API

```bash
uv run uvicorn backend.main:app --reload
```

API available at `http://127.0.0.1:8000`  
Swagger docs at `http://127.0.0.1:8000/docs`

### 4. Seed sample data (optional)

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

## Running Tests

```bash
uv run pytest
```

---

## Docker

```bash
docker build -t cygnal-app .
docker run -p 8000:8000 cygnal-app
```

---

## AI Assistance

This project was developed with the assistance of **Claude (Anthropic)**.  
AI tools were used for:

- Designing the project structure and data models
- Implementing SQLModel schemas with SQLite persistence
- Building the Streamlit dashboard with Plotly charts, free-text search, severity-colored rows, and an Edit tab
- Writing the pytest suite with fixture-based database isolation
- Generating and reviewing technical documentation

All AI-generated code was reviewed, understood, and verified locally before being committed.

---

*Created by Agneta Gavrielov — EASS-HIT 2026, Engineering of Advanced Software Solutions*