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
- `worker` – IOC refresh worker (pulls from AbuseIPDB)
- `redis` – Redis cache on port 6379

---

## ✅ Verify health

```bash
# API health
curl http://localhost:8000/health

# Redis ping
docker exec $(docker compose ps -q redis) redis-cli ping
```

---

## 🔄 Run the IOC refresh worker manually

```bash
uv run python scripts/refresh.py
```

---

## 🧪 Run tests

```bash
uv run pytest
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

---

## 🔍 View Redis keys

```bash
docker exec $(docker compose ps -q redis) redis-cli keys "ioc:seen:*"
```