# EX3 – Architecture Notes & Decisions

## Services Overview

| Service | Technology | Port | Role |
|---------|-----------|------|------|
| `api` | FastAPI + SQLModel | 8000 | Core backend, CRUD for IOCs |
| `dashboard` | Streamlit | 8501 | Visual interface for analysts |
| `worker` | Python + httpx | — | Auto-imports IOCs from AbuseIPDB |
| `ai_analyst` | FastAPI + Claude API | 8001 | AI-powered threat analysis |
| `redis` | Redis 7 Alpine | 6379 | Idempotency tracking + rate limiting |

---

## Internal Architecture

The repository keeps the course-facing service entrypoints simple while separating
implementation concerns inside each service:

- `backend/main.py` composes the FastAPI application; routes, middleware,
  configuration, schemas, database entities, repositories, and services live in
  dedicated packages.
- `frontend/dashboard.py` composes authenticated Streamlit navigation; API
  clients, reusable components, session state, data services, styles, and views
  are separated. Shared semantic color tokens follow Streamlit's live Dark,
  Light, and System theme selection.
- `ai_analyst/main.py` composes the AI microservice; routes, schemas,
  configuration, and external communication are isolated.
- `scripts/refresh.py` remains the required course entrypoint while the async
  worker implementation lives in `worker/`.
- Tests mirror the service boundaries under `tests/backend`, `tests/frontend`,
  `tests/ai_analyst`, and `tests/worker`.

This structure preserves the lecturer-facing commands while keeping composition
roots small and making individual concerns independently testable.

---

## Worker & Idempotency

The `scripts/refresh.py` worker pulls malicious IPs from **AbuseIPDB** and stores them in the database.

To prevent duplicate imports, every IOC is fingerprinted with SHA-256:

```text
fingerprint = sha256("IP:185.220.101.45")
```

The fingerprint is stored in Redis with a **24-hour TTL**:

```text
ioc:seen:<fingerprint> = "1"  (expires in 86400s)
```

The worker atomically claims each key with Redis `SET NX EX`. If another worker
already claimed it, the IOC is skipped. Processing uses bounded concurrency and
the AbuseIPDB request retries transient HTTP failures with exponential backoff.

`scripts/refresh.py` is the required course-facing entrypoint. It delegates to
the testable implementation in `worker/refresh.py` and emits one trace line per
IOC containing the generated trace ID, Redis idempotency key, and outcome:

```text
INFO worker.refresh trace_id=1adbcde0-0b88-4f55-a945-dcaed04f5190 idempotency_key=ioc:seen:07c63a... result=skipped
```

---

## AI Analyst Microservice

The `ai_analyst` service uses the **Claude API (Anthropic)** to:
- Analyze a single IOC and return a threat assessment
- Generate a summary report of all active IOCs

Start the service:
```bash
uv run uvicorn ai_analyst.main:app --port 8001
```

---

## Security Baseline

- Hashed credentials with `bcrypt` via `passlib`
- JWT-protected routes with role checks (`analyst` / `admin`)
- Token expiry set to 30 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES = 30`)
- JWTs validate issuer and audience claims
- JWT secret, issuer, audience, and expiry are environment-backed

### JWT Flow

1. `POST /auth/login` with form data `username` + `password` → returns `access_token`
2. Include header: `Authorization: Bearer <token>`
3. Protected routes verify the token and check the `role` claim

### Protected Routes

| Endpoint | Required Role |
|----------|--------------|
| `DELETE /indicators/{id}` | any authenticated user |
| `POST /indicators/{id}/deactivate` | `admin` only |

### Secret Rotation

To rotate the JWT secret:

1. Generate a new secret:
   ```bash
   openssl rand -hex 32
   ```
2. Update `JWT_SECRET_KEY` in `.env` or the deployment secret store
3. Restart the API:
   ```bash
   uv run uvicorn backend.main:app --reload
   ```
4. All existing tokens are immediately invalidated — users must log in again

---

## Enhancement – IOC Summary Report

One-click **CSV export** and **AI-generated summary** are available from the
Streamlit dashboard. The API also exposes filtered CSV export and a paginated,
ETag-enabled release-contract endpoint.

---

## Redis Trace

Actual Redis keys captured from the Compose stack on 10 June 2026:

```text
ioc:seen:07c63a564a9c290cdc88de74b6a27e7fc554d36decb88a274ef6de710978fe59
ioc:seen:dd73d89974f9ac2770eaa09906f8e5d419d45c9bdb4927bbe06f3c540ecd1f05
rate:127.0.0.1:/health:29685268
rate:testclient:/indicators/page:29685268
```

## Course Deliverables

- Compose launches API, dashboard, AI analyst, Redis, and the async worker.
- The worker has bounded concurrency, retries, atomic Redis idempotency, and
  `pytest.mark.anyio` tests.
- Redis-backed rate limiting emits the documented headers.
- Hashed credentials and issuer/audience/expiry-aware JWT role checks protect
  delete and admin deactivation routes.
- CSV export, filtering, AI reports, pagination, and ETags are covered by tests.
- Dark, Light, and browser-controlled System themes are covered by frontend
  regression tests.
- `.github/workflows/ci.yaml` and `docs/release-checklist.md` document pytest,
  coverage, Schemathesis, Ruff, mypy, MkDocs/pdoc, and FastMCP gates. The
  maintained `pdoc` package is used because legacy `pdocs` is incompatible with
  Python 3.12.
- Schemathesis intentionally fuzzes read-only GET contracts in CI so contract
  testing cannot mutate or delete grader data.

---

## AI Assistance

This project was developed with the assistance of **Claude (Anthropic)**.
All AI-generated code was reviewed, understood, and verified locally before being committed.
