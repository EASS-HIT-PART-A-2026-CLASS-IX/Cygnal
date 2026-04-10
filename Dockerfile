FROM python:3.12-slim

# Install uv inside the container
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run the server
CMD ["uv", "run", "uvicorn", "ti_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]