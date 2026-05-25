from fastapi import FastAPI

from stock_agents.core.config import get_settings
from stock_agents.core.orchestrator import AnalysisOrchestrator
from stock_agents.core.schemas import AnalysisRequest, AnalysisResponse, HealthResponse
from stock_agents.data.mock_provider import MockMarketDataProvider
from stock_agents.data.mock_social_provider import MockSocialDataProvider
from stock_agents.data.x_provider import XRecentSearchProvider

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

social_provider = (
    XRecentSearchProvider(
        bearer_token=settings.x_bearer_token,
        max_results=settings.x_recent_search_max_results,
    )
    if settings.x_bearer_token
    else MockSocialDataProvider()
)
orchestrator = AnalysisOrchestrator(
    market_data_provider=MockMarketDataProvider(),
    social_data_provider=social_provider,
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.app_env)


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze_company(request: AnalysisRequest) -> AnalysisResponse:
    return orchestrator.analyze(request)
