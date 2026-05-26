from collections.abc import Callable

from stock_agents.core.schemas import (
    AgentRoleProfile,
    AnalysisRequest,
    AnalysisResponse,
    DebateAgentOutput,
    DebateDepth,
    DebateRequest,
    DebateResponse,
    MarketSnapshot,
)
from stock_agents.llm.ollama import OllamaClient


class OllamaDebateOrchestrator:
    def __init__(
        self,
        ollama_client: OllamaClient,
        snapshot_loader: Callable[[str], MarketSnapshot],
        base_analyzer: Callable[[AnalysisRequest], AnalysisResponse],
        bull_model: str,
        bear_model: str,
        judge_model: str,
    ) -> None:
        self.ollama_client = ollama_client
        self.snapshot_loader = snapshot_loader
        self.base_analyzer = base_analyzer
        self.bull_model = bull_model
        self.bear_model = bear_model
        self.judge_model = judge_model

    def debate(self, request: DebateRequest) -> DebateResponse:
        snapshot = self.snapshot_loader(request.symbol)
        base_request = AnalysisRequest(
            symbol=request.symbol,
            horizon=request.horizon,
            risk_profile=request.risk_profile,
        )
        base_analysis = self.base_analyzer(base_request)
        context = build_company_context(snapshot, base_analysis, request.depth)
        bull_model = request.bull_model or self.bull_model
        bear_model = request.bear_model or self.bear_model
        judge_model = request.judge_model or self.judge_model

        bull_raw = self._run_bull(bull_model, context, request)
        bear_raw = self._run_bear(bear_model, context, request, bull_raw)

        for round_index in range(2, request.rounds + 1):
            bull_raw = self._run_bull(
                bull_model,
                context,
                request,
                opponent_case=bear_raw,
                round_index=round_index,
            )
            bear_raw = self._run_bear(
                bear_model,
                context,
                request,
                bull_case=bull_raw,
                round_index=round_index,
            )

        judge_raw = self._run_judge(judge_model, context, request, bull_raw, bear_raw)
        bull = parse_debate_output("bull", bull_model, bull_raw)
        bear = parse_debate_output("bear", bear_model, bear_raw)
        judge = parse_debate_output("judge", judge_model, judge_raw)
        final_decision = _extract_label(judge_raw, "DECISION") or judge.thesis
        confidence = _extract_confidence(judge_raw)

        return DebateResponse(
            symbol=snapshot.symbol,
            company_name=snapshot.company_name,
            depth=request.depth,
            rounds=request.rounds,
            base_analysis=base_analysis,
            bull_case=bull,
            bear_case=bear,
            judge=judge,
            role_profiles=role_profiles(),
            final_decision=final_decision,
            confidence=confidence,
            comparison=_extract_block_items(judge_raw, "COMPARISON"),
            missing_information=_extract_block_items(judge_raw, "MISSING_INFORMATION"),
            context=context if request.include_raw_context else None,
        )

    def _run_bull(
        self,
        model: str,
        context: str,
        request: DebateRequest,
        opponent_case: str | None = None,
        round_index: int = 1,
    ) -> str:
        prompt = bull_prompt(context, request, opponent_case, round_index)
        return self.ollama_client.generate(model=model, system=BULL_SYSTEM, prompt=prompt)

    def _run_bear(
        self,
        model: str,
        context: str,
        request: DebateRequest,
        bull_case: str,
        round_index: int = 1,
    ) -> str:
        prompt = bear_prompt(context, request, bull_case, round_index)
        return self.ollama_client.generate(model=model, system=BEAR_SYSTEM, prompt=prompt)

    def _run_judge(
        self,
        model: str,
        context: str,
        request: DebateRequest,
        bull_case: str,
        bear_case: str,
    ) -> str:
        prompt = judge_prompt(context, request, bull_case, bear_case)
        return self.ollama_client.generate(model=model, system=JUDGE_SYSTEM, prompt=prompt)


BULL_SYSTEM = (
    "You are BullAgent, a rigorous buy-side analyst. Your job is to build the strongest "
    "evidence-based case for buying the company. Be concrete, compare signals, and admit weak data. "
    "You must quantify what would make the idea attractive, not simply sound optimistic."
)

BEAR_SYSTEM = (
    "You are BearAgent, a skeptical risk analyst. Your job is to build the strongest "
    "evidence-based case against buying the company. Focus on downside, valuation, invalidation, "
    "data gaps, and better alternatives. You must distinguish real risk from generic fear."
)

JUDGE_SYSTEM = (
    "You are JudgeAgent, an investment committee chair. Compare BullAgent and BearAgent. "
    "Reward evidence quality, punish speculation, identify missing data, and issue a balanced decision. "
    "You must explain why one side is stronger for the user's investor style."
)


def role_profiles() -> list[AgentRoleProfile]:
    return [
        AgentRoleProfile(
            role="BullAgent",
            objective="Find the strongest evidence-based reason to buy or keep the company on an active buy list.",
            must_check=[
                "upside drivers and catalysts",
                "trend and support/resistance confirmation",
                "quality of fundamentals versus valuation",
                "what would invalidate the buy case",
                "whether the upside compensates for the requested margin of safety",
            ],
            decision_bias="Optimistic, but required to admit missing evidence and quantify conditions.",
        ),
        AgentRoleProfile(
            role="BearAgent",
            objective="Find the strongest reason not to buy now and expose weak assumptions in the bullish case.",
            must_check=[
                "valuation risk and margin-of-safety failure",
                "technical breakdown or false breakout risk",
                "balance-sheet and business-model fragility",
                "social/news hype versus durable information",
                "better alternatives or reasons to wait",
            ],
            decision_bias="Skeptical, but required to avoid generic objections not supported by context.",
        ),
        AgentRoleProfile(
            role="JudgeAgent",
            objective="Compare both cases as an investment committee chair and decide what is more defensible.",
            must_check=[
                "which side uses stronger evidence",
                "which claims are speculative",
                "what information is missing before capital allocation",
                "fit with horizon, risk profile, and investor style",
                "final action: STRONG_BUY, BUY, WATCH, or AVOID",
            ],
            decision_bias="Neutral; penalizes overconfidence and rewards falsifiable arguments.",
        ),
    ]


def build_company_context(
    snapshot: MarketSnapshot,
    base_analysis: AnalysisResponse,
    depth: DebateDepth,
) -> str:
    findings = "\n".join(
        f"- {finding.agent}: score={finding.score:.2f}; {finding.summary}; "
        f"evidence={'; '.join(finding.evidence)}"
        for finding in base_analysis.findings
    )
    technical = snapshot.technical_analysis
    social = snapshot.social_signal
    patterns = (
        "; ".join(f"{pattern.name} ({pattern.direction}, {pattern.confidence:.2f})" for pattern in technical.patterns)
        if technical
        else "none"
    )
    topics = ", ".join(social.key_topics) if social and social.key_topics else "none"
    depth_instruction = {
        DebateDepth.quick: "Use concise reasoning and focus on the top 3 factors.",
        DebateDepth.standard: "Use structured reasoning across fundamentals, chart, sentiment, and risk.",
        DebateDepth.deep: (
            "Use deep reasoning. Compare competing explanations, second-order effects, "
            "scenario risks, invalidation levels, and what would change the decision."
        ),
    }[depth]

    return f"""
COMPANY
Symbol: {snapshot.symbol}
Name: {snapshot.company_name}
Currency: {snapshot.currency}
Last price: {snapshot.last_price}
Market cap: {snapshot.market_cap}
P/E: {snapshot.pe_ratio}
Revenue growth: {snapshot.revenue_growth}
Debt/equity: {snapshot.debt_to_equity}
RSI14: {snapshot.rsi_14}
30d price change: {snapshot.price_change_30d}

BASE MULTI-AGENT ANALYSIS
Rating: {base_analysis.rating}
Confidence: {base_analysis.confidence}
Thesis: {base_analysis.thesis}
Findings:
{findings}
Risks: {'; '.join(base_analysis.risks)}

TECHNICAL CONTEXT
Trend: {technical.trend_direction if technical else None}
Support: {technical.support if technical else None}
Resistance: {technical.resistance if technical else None}
SMA short: {technical.sma_short if technical else None}
SMA long: {technical.sma_long if technical else None}
Patterns: {patterns}

SOCIAL CONTEXT
Platform: {social.platform if social else None}
Mentions: {social.mention_count if social else 0}
Social sentiment: {social.sentiment_score if social else None}
Engagement: {social.engagement_score if social else 0}
Topics: {topics}

ANALYSIS DEPTH
{depth_instruction}
""".strip()


def request_profile(request: DebateRequest) -> str:
    thesis = request.user_thesis or "No user thesis provided."
    return f"""
USER WORKFLOW SETTINGS
Horizon: {request.horizon}
Risk profile: {request.risk_profile}
Investor style: {request.investor_style}
Required margin of safety: {request.margin_of_safety_required:.0%}
User thesis to test: {thesis}
""".strip()


def bull_prompt(
    context: str,
    request: DebateRequest,
    opponent_case: str | None,
    round_index: int,
) -> str:
    rebuttal = f"\nOPPONENT CASE TO REBUT:\n{opponent_case}\n" if opponent_case else ""
    return f"""
Build the strongest BUY case for this company.
Round: {round_index}
{rebuttal}
{request_profile(request)}

CONTEXT:
{context}

Return exactly these sections:
THESIS: one clear buy thesis.
ARGUMENTS:
- 5 to 9 detailed arguments, each tied to data from context.
- Include catalysts, upside path, margin-of-safety argument, and invalidation level.
REBUTTALS:
- rebut the strongest bear objections if present.
EVIDENCE_REQUESTS:
- data needed to verify or falsify the bullish case.
""".strip()


def bear_prompt(
    context: str,
    request: DebateRequest,
    bull_case: str,
    round_index: int,
) -> str:
    return f"""
Build the strongest DO-NOT-BUY / SHORT-OF-CONVICTION case.
Round: {round_index}
{request_profile(request)}

BULL CASE TO CHALLENGE:
{bull_case}

CONTEXT:
{context}

Return exactly these sections:
THESIS: one clear skeptical thesis.
ARGUMENTS:
- 5 to 9 detailed arguments, each tied to data from context.
- Include downside scenarios, valuation traps, technical failure points, and data gaps.
REBUTTALS:
- directly challenge weak bullish assumptions.
EVIDENCE_REQUESTS:
- data needed to verify or falsify the bearish case.
""".strip()


def judge_prompt(context: str, request: DebateRequest, bull_case: str, bear_case: str) -> str:
    return f"""
Compare both cases and decide which is stronger for the requested investor profile.
{request_profile(request)}

CONTEXT:
{context}

BULL CASE:
{bull_case}

BEAR CASE:
{bear_case}

Return exactly these sections:
THESIS: concise final investment committee view.
DECISION: one of STRONG_BUY, BUY, WATCH, AVOID.
CONFIDENCE: decimal from 0.00 to 1.00.
ARGUMENTS:
- strongest final reasons.
COMPARISON:
- point-by-point comparison of bull vs bear evidence quality.
REBUTTALS:
- what each side failed to answer.
MISSING_INFORMATION:
- missing information that matters before real capital allocation.
WORKFLOW:
- recommended next action for the user.
""".strip()


def parse_debate_output(role: str, model: str, raw_output: str) -> DebateAgentOutput:
    return DebateAgentOutput(
        role=role,
        model=model,
        thesis=_extract_label(raw_output, "THESIS") or _first_nonempty_line(raw_output),
        arguments=_extract_block_items(raw_output, "ARGUMENTS"),
        rebuttals=_extract_block_items(raw_output, "REBUTTALS"),
        evidence_requests=_extract_block_items(raw_output, "EVIDENCE_REQUESTS"),
        raw_output=raw_output,
    )


def _extract_label(text: str, label: str) -> str | None:
    prefix = f"{label}:"
    for line in text.splitlines():
        if line.strip().upper().startswith(prefix):
            return line.split(":", 1)[1].strip()
    return None


def _extract_confidence(text: str) -> float:
    value = _extract_label(text, "CONFIDENCE")
    if value is None:
        return 0.5
    try:
        return max(0.0, min(1.0, float(value)))
    except ValueError:
        return 0.5


def _extract_block_items(text: str, label: str) -> list[str]:
    lines = text.splitlines()
    items: list[str] = []
    in_block = False
    known_labels = {
        "THESIS",
        "DECISION",
        "CONFIDENCE",
        "ARGUMENTS",
        "COMPARISON",
        "REBUTTALS",
        "EVIDENCE_REQUESTS",
        "MISSING_INFORMATION",
    }
    for line in lines:
        stripped = line.strip()
        upper = stripped.rstrip(":").upper()
        if upper == label:
            in_block = True
            continue
        if in_block and upper in known_labels:
            break
        if in_block and stripped:
            items.append(stripped.lstrip("-*0123456789. ").strip())
    return items


def _first_nonempty_line(text: str) -> str:
    return next((line.strip() for line in text.splitlines() if line.strip()), "")
