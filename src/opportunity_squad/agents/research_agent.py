"""Research Agent: pesquisa qualitativa profunda sob demanda de um produto específico."""

from __future__ import annotations

import json

from opportunity_squad.core.interfaces.agent import Agent, AgentContext, AgentResult
from opportunity_squad.core.interfaces.ai_provider import AIProvider, ModelTier
from opportunity_squad.db.models.analysis import Analysis
from opportunity_squad.db.models.product import Product
from opportunity_squad.db.session import session_scope

_SYSTEM_PROMPT = (
    "Você é um pesquisador de produto sênior. Faça uma análise qualitativa profunda do produto: "
    "pontos fortes, pontos fracos, UX, performance, potencial de IA/automação, complexidade "
    "técnica, potencial no mercado BR e internacional. Responda APENAS com JSON: "
    '{"strengths": [...], "weaknesses": [...], "ux_notes": "...", "performance_notes": "...", '
    '"copy_difficulty": "low|medium|high", "technical_complexity": "low|medium|high", '
    '"market_br_potential": <0-10>, "market_intl_potential": <0-10>, "saas_potential": <0-10>, '
    '"summary": "..."}'
)


class ResearchAgent(Agent):
    """Diferente dos demais, roda sob demanda: espera `context.data['product_id']`."""

    name = "research"

    def __init__(self, ai_provider: AIProvider):
        super().__init__()
        self._ai = ai_provider

    def run(self, context: AgentContext) -> AgentResult:
        product_id = context.data.get("product_id")
        if not product_id:
            return AgentResult(
                agent_name=self.name,
                success=False,
                error="context.data['product_id'] é obrigatório",
            )
        try:
            with session_scope() as session:
                product = session.get(Product, product_id)
                if product is None:
                    return AgentResult(
                        agent_name=self.name,
                        success=False,
                        error=f"produto {product_id} não encontrado",
                    )

                findings = self._research(product)
                if findings is None:
                    return AgentResult(
                        agent_name=self.name, success=False, error="IA não retornou JSON válido"
                    )

                analysis = (
                    session.query(Analysis)
                    .filter_by(product_id=product.id, agent_name=self.name)
                    .one_or_none()
                )
                if analysis is None:
                    analysis = Analysis(product_id=product.id, agent_name=self.name)
                    session.add(analysis)

                analysis.strengths = findings.get("strengths")
                analysis.weaknesses = findings.get("weaknesses")
                analysis.ux_notes = findings.get("ux_notes")
                analysis.performance_notes = findings.get("performance_notes")
                analysis.copy_difficulty = findings.get("copy_difficulty")
                analysis.technical_complexity = findings.get("technical_complexity")
                analysis.market_br_potential = findings.get("market_br_potential")
                analysis.market_intl_potential = findings.get("market_intl_potential")
                analysis.saas_potential = findings.get("saas_potential")
                analysis.summary = findings.get("summary")

            self.logger.info("research_completed", product_id=product_id)
            return AgentResult(agent_name=self.name, success=True, output={"product_id": product_id})
        except Exception as exc:
            self.logger.error("research_failed", error=str(exc))
            return AgentResult(agent_name=self.name, success=False, error=str(exc))

    def _research(self, product: Product) -> dict | None:
        prompt = (
            f"Produto: {product.name}\nDescrição: {product.description or product.tagline or ''}"
        )
        response = self._ai.complete(
            prompt, system=_SYSTEM_PROMPT, tier=ModelTier.DEEP, max_tokens=1200, temperature=0.3
        )
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return None
