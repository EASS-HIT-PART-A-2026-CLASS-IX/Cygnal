# Cygnal Product Specification

Cygnal is a local cyber threat intelligence product for managing Indicators of
Compromise. It combines a FastAPI and SQLModel backend, SQLite persistence,
Streamlit interface, Redis-backed worker and rate limiting, and an AI analyst
microservice.

The EX3 release must remain locally reproducible with `uv` and Docker Compose,
keep protected actions behind role-aware JWT authentication, and provide tested
filtering, CSV export, reporting, async refresh, and release-contract workflows.

The codebase uses service-level packages (`backend`, `frontend`, `ai_analyst`,
and `worker`) with small public entrypoints and internal separation between
routes, schemas, models, repositories, services, UI components, and state.
