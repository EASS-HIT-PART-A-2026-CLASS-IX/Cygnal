# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy the project configuration files
COPY pyproject.toml uv.lock README.md /app/

# Install dependencies before application code so code-only rebuilds stay fast
RUN uv sync --frozen --no-install-project --no-dev

# Copy the application code
COPY backend /app/backend
COPY frontend /app/frontend
COPY ai_analyst /app/ai_analyst
COPY worker /app/worker
COPY scripts /app/scripts

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI application
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
