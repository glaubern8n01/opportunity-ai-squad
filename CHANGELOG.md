# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Este projeto segue [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

## [0.1.0] - 2026-07-02

### Adicionado
- Núcleo (Core) com Clean Architecture: interfaces `SourceConnector`, `AIProvider`,
  `Notifier`, `ReportGenerator` e `Agent`, todas independentes de implementação (DIP).
- Sistema de plugins com auto-discovery (`plugins/registry.py`) — cada plugin vive em
  `plugins/<categoria>/<nome>/plugin.yaml` e é habilitado via `.env` (`ENABLED_*_PLUGINS`),
  sem alterar código.
- Plugins funcionais de exemplo: `github_trending` e `hacker_news` (fontes, sem
  autenticação), `anthropic` (IA), `telegram` (notificação), `markdown` (relatório).
- Schema completo do banco (21 tabelas) via SQLAlchemy 2.0 + Alembic, cobrindo sources,
  products, product_versions, reviews, competitors, market_analysis, trend_analysis,
  analyses, reports, alerts, agent_logs, runs, sources_logs, ideas, roadmaps,
  mvp_projects, features, tags, categories, watchlist e favorites.
- Os 17 agentes do squad (Scout, Discovery, Review, Sentiment, Trend, Competitor,
  Market, Gap, Strategy, MVP, Architecture, Research, Report, Notification, Memory,
  Security, Documentation) e o orquestrador (`SquadOrchestrator` + APScheduler).
- Motor de Opportunity Score (0-10) com os 13 critérios do briefing.
- Docker Compose (Postgres local + app) e Dockerfile de produção multi-stage com `uv`.
- Suíte de testes (pytest) com 18 testes cobrindo scoring, config, plugin registry,
  conectores de fonte (mockados com `respx`) e agentes (contra Postgres real).
- `.env.example`, `.gitignore`, `SECURITY.md` e checagem de segredos do Security Agent.
- MCP do Supabase configurado no escopo do projeto (`.mcp.json`), apontando para um
  banco dedicado a este projeto.

[Unreleased]: https://github.com/glaubern8n01/opportunity-ai-squad/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/glaubern8n01/opportunity-ai-squad/releases/tag/v0.1.0
