#!/bin/zsh
set -e

PROJECT_DIR="/Users/bartoszdziuba/Documents/APLIKACJA_GIELDOWA"
API_PORT="${API_PORT:-8000}"
DEMO_PORT="${DEMO_PORT:-8080}"

cd "$PROJECT_DIR"

echo "AGENT_GIE-DA local start"
echo "Project: $PROJECT_DIR"

if [ ! -d ".venv" ]; then
  echo "Creating .venv..."
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing/updating local package..."
python -m pip install -e ".[dev]"

echo "Stopping old local servers if they are running..."
lsof -ti tcp:"$API_PORT" | xargs kill -9 2>/dev/null || true
lsof -ti tcp:"$DEMO_PORT" | xargs kill -9 2>/dev/null || true

echo "Starting API on http://127.0.0.1:$API_PORT"
python -m uvicorn stock_agents.api.app:app --host 127.0.0.1 --port "$API_PORT" &
API_PID=$!

echo "Starting demo on http://127.0.0.1:$DEMO_PORT"
python -m http.server "$DEMO_PORT" --directory docs &
DEMO_PID=$!

sleep 2
open "http://127.0.0.1:$DEMO_PORT"
open "http://127.0.0.1:$API_PORT/docs"

echo ""
echo "Running:"
echo "  Demo: http://127.0.0.1:$DEMO_PORT"
echo "  API:  http://127.0.0.1:$API_PORT/docs"
echo ""
echo "Close this window or press Ctrl+C to stop."

trap 'kill "$API_PID" "$DEMO_PID" 2>/dev/null || true' INT TERM EXIT
wait
