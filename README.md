# 🛡️ Cygnal — Cyber Threat Intelligence API

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com)
[![uv](https://img.shields.io/badge/Package_Manager-uv-black)](https://github.com/astral-sh/uv)

**Cygnal** is a centralized platform for managing and sharing cyber threat indicators (IOCs).  
Built as part of the **EASS-HIT 2026** course, it enables security analysts to track malicious IPs, domains, URLs, file hashes, and email addresses — with confidence scoring, tagging, and threat actor attribution.

---

## 🌟 Key Features

- **🔍 IOC Management** – Full CRUD for threat indicators across 5 types: IP, Domain, URL, Hash, Email
- **📊 Confidence Scoring** – Rate indicator reliability from 0 to 100
- **🏷️ Tagging System** – Tag indicators with labels like `ransomware`, `APT29`, `phishing`
- **🎯 Threat Actor Attribution** – Link indicators to known threat actors
- **⏱️ Timeline Tracking** – `first_seen` / `last_seen` timestamps per indicator
- **🧪 Automated Testing** – Full pytest suite with isolated state between tests
- **🐳 Docker Ready** – Runs identically locally and in a container

---

## 🚀 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/indicators` | List all indicators |
| `POST` | `/indicators` | Create a new indicator |
| `GET` | `/indicators/{id}` | Get indicator by ID |
| `DELETE` | `/indicators/{id}` | Delete indicator |

---

## 🏗️ Project Structure

```
Cygnal/
├── cygnal/
│   └── app/
│       ├── __init__.py       # Package marker
│       ├── config.py         # Environment settings
│       ├── models.py         # Pydantic schemas (IndicatorBase, IndicatorCreate, ThreatIndicator)
│       ├── repository.py     # In-memory data layer
│       └── main.py           # FastAPI routes & app entrypoint
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures (client, clear_repository)
│   └── test_main.py          # Full test suite
├── .env.example              # Environment variable template
├── .gitignore
├── .python-version
├── Dockerfile
├── examples.http             # VS Code REST Client playground
├── seed.py                   # Sample data seeder
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI |
| Validation | Pydantic v2 |
| Storage | In-memory (Python dict) → SQLite in EX3 |
| Package Manager | uv |
| Testing | pytest + TestClient |
| Container | Docker |

---

## 🚦 Getting Started

### 1. Install uv (if not installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Sync the environment

```bash
uv sync
```

### 3. Run the API locally

```bash
uv run uvicorn cygnal.app.main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`  
Interactive docs (Swagger): `http://127.0.0.1:8000/docs`

### 4. Seed sample data (optional)

Make sure the API is running, then in a separate terminal:

```bash
uv run python seed.py
```

---

## 🧪 Running Tests

```bash
uv run pytest
```

---

## 🐳 Running with Docker

```bash
# Build
docker build -t cygnal-app .

# Run
docker run -p 8000:8000 cygnal-app
```

---

## 🤖 AI Assistance

This project was developed with the assistance of **Claude (Anthropic)**.  
AI tools were used for:

- Designing the project structure and data models
- Implementing Pydantic v2 schemas with proper field validation
- Writing the pytest suite with fixture-based state isolation
- Generating and formatting technical documentation

*All AI-generated code was reviewed, understood, and verified locally before being committed.*

---

*Created by Agneta Gavrielov for EASS-HIT 2026 — Engineering of Advanced Software Solutions*