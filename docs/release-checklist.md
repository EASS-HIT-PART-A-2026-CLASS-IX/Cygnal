# EX3 Release Checklist

Owner: Agneta Gavrielov  
Last verified: 21 June 2026

## Automated Gates

- [x] `uv run python scripts/check_release.py`
- [x] `uv sync --frozen --no-install-project`
- [x] `uvx ruff check . --no-cache`
- [x] `uvx ruff format --check . --no-cache`
- [x] `uvx --from mypy==1.19.1 mypy backend frontend ai_analyst worker scripts --ignore-missing-imports --check-untyped-defs`
- [x] pytest with backend/frontend/enrichment/worker/script coverage
- [x] `docker compose config`
- [x] service images built and full stack recreated
- [x] Schemathesis coverage and fuzzing against live OpenAPI
- [x] strict MkDocs build
- [x] pdoc backend build
- [x] FastMCP probe
- [x] `uvx pre-commit run --all-files`

## Verified Results

| Gate | Result |
| --- | --- |
| pytest | 57 passed |
| Coverage | 64% overall; enrichment service 83-100% by module |
| Ruff format | 81 files already formatted |
| Ruff lint | All checks passed |
| mypy | No issues in 68 source files |
| Schemathesis | 264 generated cases passed; 32 skipped |
| Pre-commit | Ruff, format, mypy, pytest, MkDocs all passed |
| YAML | GitHub Actions workflow parsed successfully |
| Compose | API, dashboard, enrichment, worker, Redis started |
| Free enrichment | Structured deterministic analysis returned without a key |
| Invalid IOC | Invalid IP rejected with HTTP 422 |
| Redis unavailable | API remained responsive through bounded fail-open handling |

## Demo Evidence

- [x] API, dashboard, enrichment, Redis, and worker observed running.
- [x] API and enrichment health endpoints returned `ok`.
- [x] Dashboard health endpoint returned `ok`.
- [x] Redis returned `PONG` during the healthy-stack check.
- [x] `/health` and `/indicators/page` returned trace/rate/ETag metadata.
- [x] Repeated worker execution skipped previously claimed indicators.
- [x] Worker output included trace ID, idempotency key, and result.
- [x] Analyst/admin authorization behavior is covered by passing API tests.
- [x] CSV export and structured enrichment/report flows are covered and demonstrated.
- [ ] Manually inspect the dashboard in Dark, Light, and System themes and attach
      screenshots or a short recording before submission.

## Final Submission Actions

- [ ] Review the commit plan and create the focused commits.
- [ ] Push the branch and confirm GitHub Actions passes remotely.
- [ ] Add a two-minute screen recording if pursuing the optional bonus.
