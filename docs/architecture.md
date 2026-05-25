# Architecture

AGENT_GIE-DA is organized around a small orchestration core and independent
analysis agents.

## Request Flow

1. API receives an `AnalysisRequest`.
2. Orchestrator loads market context from a provider.
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

The first version uses a deterministic in-memory provider. Real integrations
should implement the `MarketDataProvider` protocol without changing API or agent
contracts.

Social integrations implement `SocialDataProvider`. The included
`XRecentSearchProvider` uses X API v2 recent search when `X_BEARER_TOKEN` is
configured. This keeps credentials on the backend; the static GitHub Pages demo
does not expose API tokens in browser code.
