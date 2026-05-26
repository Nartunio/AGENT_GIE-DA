from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from stock_agents.agents.debate import OllamaDebateOrchestrator, role_profiles
from stock_agents.core.config import get_settings
from stock_agents.core.orchestrator import AnalysisOrchestrator
from stock_agents.core.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    DebateRequest,
    DebateResponse,
    InvestorStyle,
    HealthResponse,
)
from stock_agents.data.mock_provider import MockMarketDataProvider
from stock_agents.data.mock_social_provider import MockSocialDataProvider
from stock_agents.data.stooq_provider import StooqMarketDataProvider
from stock_agents.data.x_provider import XRecentSearchProvider
from stock_agents.llm.ollama import OllamaClient

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

mock_market_provider = MockMarketDataProvider()
market_provider = (
    StooqMarketDataProvider(
        api_key=settings.stooq_api_key,
        fallback_provider=mock_market_provider,
    )
    if settings.market_data_provider.lower() == "stooq"
    else mock_market_provider
)

social_provider = (
    XRecentSearchProvider(
        bearer_token=settings.x_bearer_token,
        max_results=settings.x_recent_search_max_results,
    )
    if settings.x_bearer_token
    else MockSocialDataProvider()
)
orchestrator = AnalysisOrchestrator(
    market_data_provider=market_provider,
    social_data_provider=social_provider,
)
ollama_client = OllamaClient(
    base_url=settings.ollama_base_url,
    timeout_seconds=settings.ollama_timeout_seconds,
)
debate_orchestrator = OllamaDebateOrchestrator(
    ollama_client=ollama_client,
    snapshot_loader=orchestrator.load_snapshot,
    base_analyzer=orchestrator.analyze,
    bull_model=settings.ollama_bull_model,
    bear_model=settings.ollama_bear_model,
    judge_model=settings.ollama_judge_model,
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.app_env)


@app.get("/api/v1/ollama/health")
def ollama_health() -> dict[str, object]:
    return {
        "available": ollama_client.is_available(),
        "base_url": settings.ollama_base_url,
        "models": {
            "bull": settings.ollama_bull_model,
            "bear": settings.ollama_bear_model,
            "judge": settings.ollama_judge_model,
        },
    }


@app.get("/api/v1/debate/options")
def debate_options() -> dict[str, object]:
    return {
        "depths": ["quick", "standard", "deep"],
        "rounds": [1, 2, 3],
        "investor_styles": [style.value for style in InvestorStyle],
        "default_margin_of_safety": 0.15,
        "default_models": {
            "bull": settings.ollama_bull_model,
            "bear": settings.ollama_bear_model,
            "judge": settings.ollama_judge_model,
        },
        "recommended_models": [
            "llama3.1:8b",
            "qwen2.5:7b",
            "mistral:7b",
            "gemma2:9b",
        ],
        "roles": [profile.model_dump() for profile in role_profiles()],
    }


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze_company(request: AnalysisRequest) -> AnalysisResponse:
    return orchestrator.analyze(request)


@app.post("/api/v1/debate", response_model=DebateResponse)
def debate_company(request: DebateRequest) -> DebateResponse:
    return debate_orchestrator.debate(request)
