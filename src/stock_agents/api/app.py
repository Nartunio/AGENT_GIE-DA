from fastapi import FastAPI

from stock_agents.core.config import get_settings
from stock_agents.core.orchestrator import AnalysisOrchestrator
from stock_agents.core.schemas import AnalysisRequest, AnalysisResponse, HealthResponse
from stock_agents.data.mock_provider import MockMarketDataProvider

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
orchestrator = AnalysisOrchestrator(market_data_provider=MockMarketDataProvider())


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.app_env)


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
def analyze_company(request: AnalysisRequest) -> AnalysisResponse:
    return orchestrator.analyze(request)
