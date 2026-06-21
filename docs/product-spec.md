# Cygnal Product Specification

Cygnal is a local cyber threat intelligence platform for managing, prioritizing,
and enriching Indicators of Compromise. It combines a FastAPI and SQLModel
backend, SQLite persistence, a Streamlit analyst workspace, Redis-backed worker
and rate limiting, and a free deterministic enrichment microservice.

The EX3 release remains reproducible with `uv` and Docker Compose. Protected
actions use role-aware JWT authentication. The platform provides tested CRUD,
filtering, CSV export, structured IOC analysis, async refresh, reporting,
pagination, ETags, and release-contract workflows.

The default enrichment mode requires no API key or paid service. An optional
local Ollama model can add a short narrative while deterministic scoring remains
the authoritative output.

The codebase uses service-level packages (`backend`, `frontend`,
`ai_analyst`, and `worker`) with small public entrypoints and separation
between routes, schemas, models, repositories, services, UI components, and
state.
