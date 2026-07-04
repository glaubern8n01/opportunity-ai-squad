"""Composition root: carrega config, monta plugins e agentes, e inicia o scheduler.

Este é o único lugar que carrega plugins para USO (injeta instâncias concretas nos
agentes). `DocumentationAgent` e `api/app.py` também referenciam `plugins.registry`,
mas só para introspecção read-only (listar plugins existentes) — nenhum dos dois
importa ou depende da lógica de negócio de um plugin específico. Todo o resto do
domínio (agents, scoring) depende apenas das interfaces em `core.interfaces`.
"""

from __future__ import annotations

from opportunity_squad.agents import (
    ArchitectureAgent,
    CompetitorAgent,
    DiscoveryAgent,
    DocumentationAgent,
    GapAgent,
    MarketAgent,
    MemoryAgent,
    MvpAgent,
    NotificationAgent,
    ReportAgent,
    ResearchAgent,
    ReviewAgent,
    ScoutAgent,
    SecurityAgent,
    SentimentAgent,
    StrategyAgent,
    TrendAgent,
)
from opportunity_squad.core.config import Settings, get_settings
from opportunity_squad.core.interfaces.agent import Agent
from opportunity_squad.core.logging import configure_logging, get_logger
from opportunity_squad.scheduler.jobs import SquadOrchestrator, build_scheduler

logger = get_logger("main")


def _source_plugin_config(settings: Settings) -> dict[str, dict]:
    return {
        "github_trending": {"token": settings.github_token},
        "hacker_news": {},
        "scrapegraph_ai": {"api_key": settings.scrapegraph_api_key},
    }


def _ai_plugin_config(settings: Settings) -> dict[str, dict]:
    return {
        "anthropic": {
            "api_key": settings.anthropic_api_key,
            "model_cheap": settings.anthropic_model_cheap,
            "model_standard": settings.anthropic_model,
            "model_deep": settings.anthropic_model_deep,
        }
    }


def _notification_plugin_config(settings: Settings) -> dict[str, dict]:
    return {
        "telegram": {
            "bot_token": settings.telegram_bot_token,
            "chat_id": settings.telegram_chat_id,
        }
    }


def build_agents(settings: Settings) -> dict[str, Agent]:
    from plugins.registry import load_enabled

    sources = load_enabled(
        "sources", settings.enabled_source_plugins, _source_plugin_config(settings)
    )
    ai_providers = load_enabled("ai", settings.enabled_ai_plugins, _ai_plugin_config(settings))
    notifiers = load_enabled(
        "notifications", settings.enabled_notification_plugins, _notification_plugin_config(settings)
    )
    report_generators = load_enabled("reports", settings.enabled_report_plugins)

    ai_provider = next(iter(ai_providers.values()), None)
    notifier = next(iter(notifiers.values()), None)
    report_generator = next(iter(report_generators.values()), None)

    agents: dict[str, Agent] = {
        "scout": ScoutAgent(sources),
        "discovery": DiscoveryAgent(),
        "review": ReviewAgent(sources),
        "security": SecurityAgent(),
        "memory": MemoryAgent(),
        "documentation": DocumentationAgent(),
    }

    if ai_provider is not None:
        agents.update(
            {
                "sentiment": SentimentAgent(ai_provider),
                "trend": TrendAgent(),
                "competitor": CompetitorAgent(ai_provider),
                "market": MarketAgent(ai_provider),
                "gap": GapAgent(ai_provider),
                "strategy": StrategyAgent(ai_provider),
                "mvp": MvpAgent(ai_provider),
                "architecture": ArchitectureAgent(ai_provider),
                "research": ResearchAgent(ai_provider),
            }
        )
    else:
        logger.warning("ai_provider_not_configured", detail="agentes de IA desabilitados")
        agents["trend"] = TrendAgent()

    if report_generator is not None:
        agents["report"] = ReportAgent(report_generator)
    else:
        logger.warning("report_generator_not_configured", detail="Report Agent desabilitado")

    if notifier is not None:
        agents["notification"] = NotificationAgent(notifier)
    else:
        logger.warning("notifier_not_configured", detail="Notification Agent desabilitado")

    return agents


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("startup", app_env=settings.app_env)

    agents = build_agents(settings)
    orchestrator = SquadOrchestrator(agents)
    scheduler = build_scheduler(orchestrator, settings)

    logger.info("scheduler_starting", jobs=[job.id for job in scheduler.get_jobs()])
    scheduler.start()


if __name__ == "__main__":
    main()
