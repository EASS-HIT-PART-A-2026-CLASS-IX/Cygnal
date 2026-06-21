# EX3 Architecture Notes and Evidence

## Services

| Service | Technology | Port | Responsibility |
| --- | --- | --- | --- |
| `api` | FastAPI, SQLModel, SQLite | 8000 | IOC validation, CRUD, auth, contracts |
| `dashboard` | Streamlit, Plotly | 8501 | Analyst threat feed and workflows |
| `worker` | asyncio, httpx | - | IOC ingestion, retries, concurrency |
| `ai_analyst` | FastAPI | 8001 | Free structured IOC enrichment |
| `redis` | Redis 7 | 6379 | Rate limiting and idempotency |

The packages are separated by service while preserving the lecturer-facing
entrypoints: `backend/main.py`, `frontend/dashboard.py`,
`scripts/refresh.py`, and `ai_analyst/main.py`.

## Async Worker and Redis Idempotency

The worker:

- uses `asyncio.Semaphore` for bounded concurrency;
- retries transient HTTP failures with exponential backoff;
- fingerprints each IOC with SHA-256;
- claims `ioc:seen:<fingerprint>` atomically with Redis `SET NX EX`;
- deletes the claim when persistence fails so work can be retried;
- emits a trace ID, idempotency key, and result for every entry.

Example trace captured from the local Compose stack:

```text
INFO worker.refresh trace_id=d04563a8-5ab2-4d0d-bc7e-3718e8472e80 idempotency_key=ioc:seen:5f7dba... result=added
```

`tests/worker/test_refresh.py` covers concurrency, retry behavior, and the atomic
Redis claim using `pytest.mark.anyio`.

## Free Enrichment Enhancement

The enrichment service is useful without a paid provider or API key. Its
deterministic engine combines severity, confidence, active state, relevant tags,
IOC type, source, and database history. `POST /analyze` returns:

- risk score and risk level;
- structured reasoning;
- analysis confidence;
- IOC-type and source context;
- first-seen age and matching-record count;
- recommended analyst actions.

Ollama is optional. When `OLLAMA_BASE_URL` is configured and available, a local
model adds a short explanation. Provider errors are caught and the complete
structured deterministic result is returned unchanged.

Tests cover successful structured analysis, invalid IDs, missing indicators,
backend errors, optional local-model success, and local-model fallback.

## Security Baseline

- Passwords are hashed with bcrypt through Passlib.
- JWTs validate expiration, issuer, audience, subject, and role.
- Permanent deletion requires authentication.
- Deactivation requires the `admin` role.
- Tests cover missing authentication, expired tokens, and insufficient role.
- IOC creation rejects undeclared fields and invalid IP/domain/URL/hash/email
  formats.

### Secret Rotation

1. Generate a new key: `openssl rand -hex 32`.
2. Replace `JWT_SECRET_KEY` in the local environment or deployment secret store.
3. Restart the API.
4. Existing tokens become invalid and users must authenticate again.

Classroom credentials and fallback secrets must not be reused outside the local
demonstration.

## Release Contracts

- deterministic ID-ordered listings;
- page metadata and `X-Total-Count`;
- weak ETags and `If-None-Match` / 304 behavior;
- filtered CSV export;
- shared trace and rate-limit headers;
- documented error envelopes;
- FastMCP repository bridge.

## Course Deliverables

- Compose launches API, dashboard, enrichment, Redis, and worker services.
- The dashboard provides list/create, search, filtering, edit/delete, CSV,
  metrics, and structured enrichment workflows.
- Worker reliability, JWT role checks, contracts, and enhancements have automated
  coverage.
- CI runs formatting, Ruff, mypy, pytest/coverage, Schemathesis, MkDocs, pdoc,
  and the MCP probe.
- `scripts/demo.sh` provides a grader-oriented local walkthrough.

## AI Assistance Disclosure

Claude and OpenAI Codex assisted with design review, implementation, testing, and
documentation. Generated changes were reviewed and verified locally. Runtime
analysis is deterministic by default and does not depend on a paid AI service.
