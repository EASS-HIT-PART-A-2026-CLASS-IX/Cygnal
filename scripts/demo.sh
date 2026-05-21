#!/bin/bash
echo "=== Cygnal Demo ==="
echo ""
echo "Step 1: Starting API..."
uv run uvicorn backend.main:app --reload &
API_PID=$!
sleep 2

echo ""
echo "Step 2: Seeding sample data..."
uv run python seed.py

echo ""
echo "Step 3: Health check..."
curl -s http://127.0.0.1:8000/health | python3 -m json.tool

echo ""
echo "Step 4: List indicators..."
curl -s http://127.0.0.1:8000/indicators | python3 -m json.tool

echo ""
echo "Step 5: Login and get JWT token..."
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -d "username=analyst&password=analyst123" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Token: ${TOKEN:0:50}..."

echo ""
echo "Step 6: Starting Streamlit dashboard..."
echo "Open http://localhost:8501 in your browser"
uv run streamlit run frontend/dashboard.py &

echo ""
echo "=== Demo running ==="
echo "API:       http://127.0.0.1:8000/docs"
echo "Dashboard: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
wait $API_PID
