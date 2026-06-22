# Docker Compose Runbook

## Prerequisites

- Docker Desktop running
- Docker Compose v2
- Ports 8000, 8001, 8501, and 6379 available

## Launch

```bash
docker compose up --build
```

Services:

- `api`: http://localhost:8000
- `ai_analyst`: http://localhost:8001
- `dashboard`: http://localhost:8501
- `redis`: localhost:6379
- `worker`: idempotent demo seed, then scheduled IOC refresh every five minutes

## Verify

```bash
docker compose ps
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8501/_stcore/health
docker compose exec -T redis redis-cli ping
```

Expected: API and enrichment report `ok`, Streamlit reports `ok`, and Redis
returns `PONG`. The initial feed contains varied IP, domain, URL, hash, and
email examples; rerunning Compose does not duplicate them.

## Exercise Free Enrichment

Choose an existing indicator ID:

```bash
curl -s -X POST http://localhost:8001/analyze   -H "Content-Type: application/json"   -d '{"indicator_id": 1}'
```

No API key is required.

Optional Ollama on Docker Desktop:

```bash
ollama pull llama3.2:3b
export OLLAMA_BASE_URL=http://host.docker.internal:11434
docker compose up --build -d ai_analyst
```

If Ollama is stopped or unavailable, deterministic enrichment continues to work.

## Worker and Redis Evidence

```bash
docker compose run --rm worker sh -c "uv run python scripts/refresh.py"
docker compose exec -T redis redis-cli --scan --pattern "ioc:seen:*"
docker compose exec -T redis redis-cli --scan --pattern "rate:*"
docker compose logs --tail=30 worker
```

A repeated worker run should report skipped indicators while the idempotency keys
remain valid.

## Headers and Contracts

```bash
curl -i http://localhost:8000/health
curl -i "http://localhost:8000/indicators/page?page=1&page_size=3"
```

Responses expose trace and rate-limit headers; the paginated endpoint also
returns `X-Total-Count` and `ETag`.

## Tests and Release Gates

```bash
uv run pytest
uv run python scripts/check_release.py
```

The release runner expects the API at http://127.0.0.1:8000 for Schemathesis.

## Stop

```bash
docker compose down
```

Use docker compose down -v only when you intentionally want to reset the
persisted demonstration database.
