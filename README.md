# AGENT_GIE-DA

Multi-agent system for stock market company analysis.

The project starts as a pragmatic Python/FastAPI backend with a clean agent
boundary. The initial version uses deterministic placeholder agents so the
application can be tested and extended before paid market-data or LLM providers
are connected.

## What Is Included

- FastAPI HTTP API.
- Multi-agent orchestration layer.
- Separate agents for fundamentals, technicals, sentiment, risk, and final
  synthesis.
- Typed request/response models.
- Provider interfaces for future market data and LLM integrations.
- Docker and Docker Compose setup.
- Pytest test suite.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn stock_agents.api.app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Docker

```bash
docker compose up --build
```

## Example Request

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","horizon":"medium","risk_profile":"balanced"}'
```

## Project Layout

```text
src/stock_agents/
  agents/      Individual analysis agents
  api/         FastAPI application
  core/        Settings, schemas, orchestration
  data/        Market-data provider interfaces and stubs
tests/         Unit and API tests
docs/          Architecture notes
```

## Next Milestones

1. Add real market-data providers.
2. Add LLM-backed agent implementations.
3. Persist analysis runs in a database.
4. Add portfolio/watchlist workflows.
5. Add frontend dashboard.
