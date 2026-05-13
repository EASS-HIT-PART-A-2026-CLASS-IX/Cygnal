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
- **⏱️ Timeline Tracking** – `created_at` timestamp per indicator
- **🧪 Automated Testing** – Full pytest suite with isolated state between tests
- **🐳 Docker Ready** – Runs identically locally and in a container
- **📊 Streamlit Dashboard** – Visual interface for managing and exploring IOCs
- **📥 CSV Export** – One-click export of all indicators

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
├── backend/
│   ├── init.py           # Package marker
│   ├── config.py             # Environment settings
│   ├── database.py           # SQLite + SQLModel engine
│   ├── models.py             # SQLModel schemas (Indicator, IndicatorCreate)
│   ├── repository.py         # Database operations
│   └── main.py               # FastAPI routes & app entrypoint
├── frontend/
│   ├── init.py           # Package marker
│   ├── client.py             # Typed HTTP client (httpx)
│   └── dashboard.py          # Streamlit dashboard
├── tests/
│   ├── init.py
│   ├── conftest.py           # Pytest fixtures (client, in-memory DB)
│   ├── test_main.py          # Backend API test suite
│   └── test_frontend.py      # Frontend client test suite
├── .env.example              # Environment variable template
├── .gitignore
├── .python-version
├── Dockerfile
├── docker-compose.yml
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
| Validation | Pydantic v2 + SQLModel |
| Storage | SQLite |
| Frontend | Streamlit |
| HTTP Client | httpx |
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
uv run uvicorn backend.main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`  
Interactive docs (Swagger): `http://127.0.0.1:8000/docs`

### 4. Seed sample data (optional)

Make sure the API is running, then in a separate terminal:

```bash
uv run python seed.py
```

---

## 🖥️ Running API + Dashboard Together

Open two separate terminals:

**Terminal 1 – Start the API:**
```bash
uv run uvicorn backend.main:app --reload
```

**Terminal 2 – Start the Streamlit dashboard:**
```bash
uv run streamlit run frontend/dashboard.py
```

Then open your browser at:
- API docs (Swagger): `http://127.0.0.1:8000/docs`
- Cygnal Dashboard: `http://localhost:8501`

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
- Implementing SQLModel schemas with SQLite persistence
- Building the Streamlit dashboard and typed HTTP client
- Writing the pytest suite with fixture-based DB isolation
- Generating and formatting technical documentation

*All AI-generated code was reviewed, understood, and verified locally before being committed.*

---

*Created by Agneta Gavrielov for EASS-HIT 2026 — Engineering of Advanced Software Solutions*