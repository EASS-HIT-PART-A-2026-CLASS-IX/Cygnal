# EX3 Release Checklist

Owner: Agneta Gavrielov

## Required Gates

- [ ] `uv run python scripts/check_release.py` (cross-platform aggregate runner)
- [ ] `uv sync --frozen`
- [ ] `uvx ruff check .`
- [ ] `uvx --from mypy==1.19.1 mypy backend frontend ai_analyst worker scripts --ignore-missing-imports --check-untyped-defs`
- [ ] `uv run --with pytest-cov pytest --cov=backend --cov=frontend --cov=ai_analyst --cov=worker --cov=scripts --cov-report=term-missing`
- [ ] `docker compose config`
- [ ] `docker compose up --build`
- [ ] `uvx schemathesis run http://localhost:8000/openapi.json --checks status_code_conformance,response_schema_conformance --include-method GET --exclude-path /auth/me --phases coverage,fuzzing --max-examples 5 --generation-database :memory:`
- [ ] `uvx --from mkdocs-material mkdocs build --strict`
- [ ] `uv run --with pdoc pdoc backend -o site/api`
- [ ] `uv run --no-sync --with "mcp[cli]>=1.1.0" python -m scripts.mcp_probe`
- [ ] `uvx pre-commit run --all-files`

## Demo Evidence

- [ ] API, dashboard, AI analyst, Redis, and worker are visible in `docker compose ps`.
- [ ] `/health` and `/indicators/page` show trace, rate-limit, total-count, and ETag headers.
- [ ] A second worker run skips previously claimed indicators.
- [ ] Analyst receives `403` from the admin route; admin succeeds.
- [ ] CSV export and AI report are demonstrated.
- [ ] Dashboard navigation and login are checked in Dark, Light, and System themes.
- [ ] Redis `ioc:seen:*` and `rate:*` key excerpts are pasted into `docs/EX3-notes.md`.
- [ ] Worker output shows `trace_id`, `idempotency_key`, and result together.
