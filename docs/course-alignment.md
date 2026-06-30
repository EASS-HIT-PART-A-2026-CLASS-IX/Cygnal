# Course Alignment Checklist

This checklist maps the current Cygnal implementation to the published EASS-HIT
EX1-EX3 requirements.

## EX1 - FastAPI Foundations

| Requirement | Status | Evidence | Submission risk |
| --- | --- | --- | --- |
| Core-resource CRUD | Fully implemented | `backend/api/routes/indicators.py` | Low |
| Pydantic validation | Fully implemented | Typed schemas and IOC-specific validation | Low |
| pytest/TestClient coverage | Fully implemented | `tests/backend/test_api.py` | Low |
| README run/test guidance | Fully implemented | Root `README.md` | Low |
| Seed or HTTP playground bonus | Fully implemented | `scripts/seed.py`, `examples.http` | Low |

## EX2 - Friendly Interface

| Requirement | Status | Evidence | Submission risk |
| --- | --- | --- | --- |
| Interface calls EX1 API | Fully implemented | `frontend/api/client.py` | Low |
| List and add workflow | Fully implemented | Threat Feed and Add Indicator pages | Low |
| Clear user guidance | Fully implemented | Page headers, validation, feedback | Low |
| Small useful extra | Fully implemented | Search, metrics, edit/delete, CSV | Low |
| Automated interface workflow bonus | Fully implemented | Streamlit navigation/client/style tests | Low |

## EX3 - Full-Stack Microservices

| Requirement | Status | Evidence | Submission risk |
| --- | --- | --- | --- |
| Three or more cooperating services | Fully implemented | API, dashboard, worker, enrichment, Redis | Low |
| Compose and runbook | Fully implemented | `compose.yaml`, `docs/runbooks/compose.md` | Low |
| Bounded concurrency and retries | Fully implemented | `worker/refresh.py` | Low |
| Redis idempotency and trace evidence | Fully implemented | Worker tests and `docs/EX3-notes.md` | Low |
| `pytest.mark.anyio` worker test | Fully implemented | `tests/worker/test_refresh.py` | Low |
| Password hashing and JWT role checks | Fully implemented | Backend security/auth modules | Low |
| Expiry and missing-role tests | Fully implemented | Backend API tests | Low |
| Thoughtful enhancement | Fully implemented | Structured free IOC enrichment and CTI feed | Low |
| Automated enhancement tests | Fully implemented | AI fallback/structure/error tests | Low |
| Local demo script | Fully implemented | `scripts/demo.sh` | Low |
| Pagination, ETag, CSV | Fully implemented | Indicator contracts and tests | Low |
| Ruff, mypy, pytest, Schemathesis, docs | Fully implemented | CI and release runner | Low |
| FastMCP bridge | Implemented | `scripts/indicators_mcp.py`, probe script | Medium: probe is lightweight |
| Two-minute recording bonus | Provided | Demo video: https://youtu.be/tfJD0_qhUn8 | Bonus only |

## Remaining Academic Risks

- Replace classroom JWT credentials/secrets for any environment beyond the local demo.
- The FastMCP bridge is intentionally lightweight and used as a small integration
  enhancement rather than a primary product workflow.
