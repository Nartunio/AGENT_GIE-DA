# Architecture

AGENT_GIE-DA is organized around a small orchestration core and independent
analysis agents.

## Request Flow

1. API receives an `AnalysisRequest`.
2. Orchestrator loads market context from a provider such as Stooq or the mock provider.
3. Orchestrator optionally loads social context from providers such as X.
4. Specialized agents produce partial analyses.
5. Synthesis agent combines results into one decision-oriented report.
6. API returns an `AnalysisResponse`.

## Agent Roles

- `FundamentalAgent`: business quality, profitability, leverage, valuation.
- `TechnicalAgent`: trend, momentum, support/resistance context.
- `SentimentAgent`: news and market narrative.
- `SentimentAgent`: news, social-media discussion, topics, and engagement.
- `RiskAgent`: downside risks, uncertainty, liquidity, macro sensitivity.
- `SynthesisAgent`: combines signals and produces final rating.

## Provider Boundary

The app includes a deterministic in-memory provider and a Stooq CSV provider.
Stooq requires a free API key for automated CSV downloads, configured as
`STOOQ_API_KEY`. Market-data integrations implement the `MarketDataProvider`
protocol without changing API or agent contracts.

## Chart Analysis

Market snapshots can include `price_history` and `technical_analysis`. The
technical analysis layer calculates SMA20, SMA50, trend direction, support,
resistance, chart overlays, and pattern hints. `TechnicalAgent` uses those
signals in its score and evidence, while the GitHub Pages demo renders the same
concept visually as an SVG chart.

## Ollama Debate

The Ollama debate layer is intentionally separated from the fast deterministic
analysis endpoint. `/api/v1/debate` first builds the ordinary multi-agent
snapshot, then sends the same context to three local model roles:

- `BullAgent` argues for buying.
- `BearAgent` argues against buying.
- `JudgeAgent` compares both cases and returns the final decision.

The request controls analysis depth, number of rounds, and model names for each
role. This keeps ordinary analysis responsive while allowing deeper local
reasoning when Ollama is running.

Social integrations implement `SocialDataProvider`. The included
`XRecentSearchProvider` uses X API v2 recent search when `X_BEARER_TOKEN` is
configured. This keeps credentials on the backend; the static GitHub Pages demo
does not expose API tokens in browser code.
