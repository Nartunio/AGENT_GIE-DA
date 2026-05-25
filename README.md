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
- Optional X recent-search ingestion for social sentiment analysis.
- Optional Stooq CSV market-data ingestion with no API key required.
- Technical chart analysis with trend lines, support, resistance, moving
  averages, and pattern hints.
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

## Desktop Launcher

On macOS you can run the local demo and API with:

```bash
./scripts/start_local.command
```

The launcher starts:

- demo page: `http://127.0.0.1:8080`
- API docs: `http://127.0.0.1:8000/docs`

It also exists on the Desktop as `AGENT_GIE-DA-start.command` for quick launch.

## Docker

```bash
docker compose up --build
```

## GitHub Pages Demo

The repository includes a static browser demo in `docs/index.html`. It provides
a company input field and generates a multi-agent report directly in the
browser.

To publish it on GitHub:

1. Open repository `Settings`.
2. Go to `Pages`.
3. Set source to `Deploy from a branch`.
4. Select branch `main` and folder `/docs`.
5. Save.

The demo is intentionally deterministic and does not yet fetch live market data.
It is a frontend shell for the agent workflow.

The demo also renders a technical chart with:

- price line for the last 90 sessions,
- SMA20 and SMA50,
- trend line,
- support and resistance levels,
- pattern hints such as resistance tests, support tests, and moving-average
  alignment.

## X Social Data

The backend can enrich a company report with recent public posts from X. Set a
Bearer Token in `.env`:

```bash
X_BEARER_TOKEN=your_x_api_bearer_token
X_RECENT_SEARCH_MAX_RESULTS=20
```

When the token is present, the API uses X API v2 recent search:

```text
GET https://api.x.com/2/tweets/search/recent
```

It requests recent posts matching the company name, ticker, or cashtag, then
normalizes post text, public engagement metrics, topics, and sentiment into the
sentiment agent. Without a token, the app uses a deterministic mock social
provider so local development and tests keep working.

## Free Market Data

The backend includes a Stooq provider for free public OHLCV market data. Stooq
currently requires a free API key for automated CSV downloads. It uses this CSV
download endpoint:

```text
https://stooq.com/q/d/l/?s={symbol}&d1={YYYYMMDD}&d2={YYYYMMDD}&i=d
```

Enable it in `.env`:

```bash
MARKET_DATA_PROVIDER=stooq
STOOQ_API_KEY=your_free_stooq_api_key
```

Supported aliases include `AAPL`, `MSFT`, `CDR`, `CD PROJEKT`, `PKO`, `PKO BP`,
`PKN`, and `ORLEN`. Unknown symbols default to the Warsaw suffix `.pl`; explicit
Stooq-style symbols such as `aapl.us` or `cdr.pl` can also be passed. If Stooq is
temporarily unavailable, the app falls back to the deterministic mock provider.

To get the free Stooq key, open a URL such as:

```text
https://stooq.com/q/d/?s=aapl.us&get_apikey
```

Enter the captcha, then copy the value after `apikey=` from the generated CSV
download link.

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
