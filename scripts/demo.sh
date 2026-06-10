#!/bin/bash
set -euo pipefail

echo "=== Cygnal Demo ==="

echo "Step 1: Start the complete Compose stack"
docker compose up --build -d

echo "Step 2: Wait for API health"
until curl -fsS http://127.0.0.1:8000/health >/dev/null; do sleep 1; done
docker compose ps

echo "Step 3: Verify trace and Redis-backed rate-limit headers"
curl -si http://127.0.0.1:8000/health

echo "Step 4: Show paginated contract and CSV enhancement"
curl -s "http://127.0.0.1:8000/indicators/page?page=1&page_size=3" | python3 -m json.tool
curl -s "http://127.0.0.1:8000/indicators/export.csv" | head -n 4

echo "Step 5: Verify JWT role protection"
ANALYST_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -d "username=analyst&password=analyst123" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
ADMIN_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -d "username=admin&password=admin123" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
INDICATOR_ID=$(curl -s http://127.0.0.1:8000/indicators | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['id'])")
curl -si -X POST "http://127.0.0.1:8000/indicators/${INDICATOR_ID}/deactivate" \
  -H "Authorization: Bearer ${ANALYST_TOKEN}" | head -n 1
curl -si -X POST "http://127.0.0.1:8000/indicators/${INDICATOR_ID}/deactivate" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | head -n 1

echo "Step 6: Show worker idempotency and Redis evidence"
docker compose run --rm worker sh -c "uv run python scripts/refresh.py"
docker compose exec -T redis redis-cli --scan --pattern "ioc:seen:*"
docker compose exec -T redis redis-cli --scan --pattern "rate:*"

echo "Step 7: Exercise the AI report enhancement"
curl -s -X POST http://127.0.0.1:8001/report | python3 -m json.tool

echo "Dashboard: http://localhost:8501"
echo "API docs:  http://localhost:8000/docs"
echo "AI docs:   http://localhost:8001/docs"
echo "Stop with: docker compose down"
