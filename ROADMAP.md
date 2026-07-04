# Roadmap

## v0.1.0 — Fundação (concluído)
- [x] Core com Clean Architecture (interfaces de Source/AIProvider/Notifier/ReportGenerator/Agent)
- [x] Sistema de plugins com auto-discovery
- [x] Schema completo (21 tabelas) + Alembic
- [x] 17 agentes + orquestrador + APScheduler
- [x] Plugins funcionais: github_trending, hacker_news, anthropic, telegram, markdown
- [x] Docker Compose + Dockerfile
- [x] Testes automatizados (pytest) + lint (ruff) + type-check (mypy)
- [x] MCP do Supabase configurado no escopo do projeto

## v0.2.0 — Mais fontes de dados
- [x] Plugin `scrapegraph_ai` (extração estruturada via API hospedada da
      ScrapeGraphAI — cobre fontes sem API oficial, sem scraping direto/agressivo)
- [ ] Plugin `reddit` (OAuth client_credentials, API oficial)
- [ ] Plugin `product_hunt` (GraphQL API oficial, requer developer token)
- [ ] Plugin `google_play` / `app_store` (metadados públicos de apps)
- [ ] Plugin `indie_hackers` / `hacker_news` (expandir cobertura de comentários)
- [ ] Plugin `g2` / `capterra` / `trustpilot` (reviews — respeitando ToS/APIs oficiais)

## v0.3.0 — Observabilidade e confiabilidade
- [ ] Endpoint `/runs` e `/opportunities` na API FastAPI (hoje só `/health` e `/plugins`)
- [ ] Retry/backoff configurável por plugin via `plugin.yaml`
- [ ] Dashboard web read-only (plugins/dashboards/web)
- [ ] Alertas de falha de execução recorrente (Notification Agent -> Telegram)
- [ ] Backups automáticos do Postgres (Supabase) documentados em docs/database/

## v0.4.0 — Exportação e integrações
- [ ] Plugin de export CSV/Excel
- [ ] Plugin de export Notion
- [ ] Newsletter automática (TLDR/Ben's Bites style) a partir dos relatórios

## Ideias futuras (sem data)
- [ ] Segundo provedor de IA (OpenAI/Gemini) implementando `AIProvider`
- [ ] Canal de notificação Discord/Slack/E-mail
- [ ] Autenticação multi-usuário para watchlist/favorites (hoje single-tenant)
- [ ] Geração de relatório em PDF/HTML além do Markdown

Ver também [TODO.md](TODO.md) para itens técnicos de curto prazo e
[MEMORY.md](MEMORY.md) para o histórico de decisões e progresso sessão a sessão.
