# 🛡️ Cygnal - Threat Intelligence API

This is the core backend microservice for managing cyber threat indicators, developed as part of **EX1 - FastAPI Foundations**.

## Project Overview
The service allows security analysts to manage threat indicators (IPs, Domains, URLs, etc.) using a RESTful API.
- **Backend Framework:** FastAPI
- **Data Validation:** Pydantic
- **Storage:** In-memory (Python Dictionary)
- **Dependency Injection:** Implemented for the Repository layer using FastAPI's `Depends`.

## Setup Instructions (using uv)

1. **Install uv** (if not already installed):
```bash
curl -LsSf https://astral-sh/uv/install.sh | sh
```

2. **Sync the environment**:
```bash
uv sync
```

## Running the API Locally
Start the server with auto-reload:
```bash
uv run uvicorn ti_service.app.main:app --reload
```
The interactive Swagger documentation is available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Running Tests
To run the automated test suite using `pytest`:
```bash
export PYTHONPATH=$PYTHONPATH:.
uv run pytest
```

## Running with Docker
1. **Build the Docker image**:
```bash
docker build -t threat-intel-app .
```

2. **Run the container**:
```bash
docker run -p 8000:8000 threat-intel-app
```

## Development Tools
- **.http Playground:** Use `examples.http` in VS Code for rapid API testing (Bonus Feature).
- **Dependency Injection:** The `get_repo` dependency ensures modularity and testability.
