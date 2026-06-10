# 🐳 Compose Runbook – Cygnal

## Prerequisites

- Docker Desktop installed and running
- WSL2 enabled (Windows users)

---

## 🚀 Launch the full stack

```bash
docker compose up --build
```

This starts:
- `api` – FastAPI backend on port 8000
- `dashboard` – Streamlit frontend on port 8501
- `ai_analyst` – AI analysis microservice on port 8001
- `worker` – async IOC refresh worker, repeated every five minutes
- `redis` – Redis cache on port 6379

---

## ✅ Verify health

```bash
# API health
curl http://localhost:8000/health

# Redis ping
docker exec $(docker compose ps -q redis) redis-cli ping

# Full service status
docker compose ps
```

---

## 🔄 Run the IOC refresh worker manually

```bash
docker compose run --rm worker sh -c "uv run python scripts/refresh.py"
```

---

## 🧪 Run tests

```bash
uv run pytest

# CI-equivalent contract probe
uvx schemathesis run http://localhost:8000/openapi.json --checks status_code_conformance,response_schema_conformance --include-method GET --exclude-path /auth/me --phases coverage,fuzzing --max-examples 5 --generation-database :memory:
```

---

## 🛑 Stop the stack

```bash
docker compose down
```

---

## 📋 Rate limit headers

Every API response includes:
- `X-RateLimit-Limit` – max requests per minute
- `X-RateLimit-Remaining` – remaining requests

Verify them together with trace and ETag headers:

```bash
curl -i http://localhost:8000/health
curl -i "http://localhost:8000/indicators/page?page=1&page_size=3"
```

---

## 🔍 View Redis keys

```bash
docker exec $(docker compose ps -q redis) redis-cli keys "ioc:seen:*"
docker exec $(docker compose ps -q redis) redis-cli keys "rate:*"
```

## CI and release gates

GitHub Actions runs pytest with coverage, Ruff, mypy, Schemathesis, MkDocs,
pdocs, and the FastMCP probe. The complete local checklist is in
`docs/release-checklist.md`.
