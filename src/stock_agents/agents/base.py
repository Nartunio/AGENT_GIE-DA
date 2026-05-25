from abc import ABC, abstractmethod

from stock_agents.core.schemas import AgentFinding, AnalysisRequest, MarketSnapshot


class AnalysisAgent(ABC):
    name: str

    @abstractmethod
    def analyze(self, snapshot: MarketSnapshot, request: AnalysisRequest) -> AgentFinding:
        """Return the agent-specific finding for a company snapshot."""
