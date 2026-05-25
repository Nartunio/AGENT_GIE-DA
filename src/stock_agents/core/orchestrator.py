from stock_agents.agents.fundamental import FundamentalAgent
from stock_agents.agents.risk import RiskAgent
from stock_agents.agents.sentiment import SentimentAgent
from stock_agents.agents.synthesis import SynthesisAgent
from stock_agents.agents.technical import TechnicalAgent
from stock_agents.core.schemas import AnalysisRequest, AnalysisResponse
from stock_agents.data.provider import MarketDataProvider


class AnalysisOrchestrator:
    def __init__(self, market_data_provider: MarketDataProvider) -> None:
        self.market_data_provider = market_data_provider
        self.agents = [
            FundamentalAgent(),
            TechnicalAgent(),
            SentimentAgent(),
            RiskAgent(),
        ]
        self.synthesis_agent = SynthesisAgent()

    def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        snapshot = self.market_data_provider.get_snapshot(request.symbol)
        findings = [agent.analyze(snapshot, request) for agent in self.agents]
        return self.synthesis_agent.synthesize(snapshot, request, findings)
