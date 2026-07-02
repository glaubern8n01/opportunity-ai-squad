# TODO

Itens técnicos de curto prazo. Para visão de produto/versões, ver [ROADMAP.md](ROADMAP.md).

## Bloqueado / aguardando o usuário
- [ ] Concluir autenticação OAuth do MCP do Supabase (`claude /mcp` → selecionar `supabase`)
- [ ] Aplicar a migration inicial (`alembic upgrade head`) no projeto Supabase real,
      após obter a connection string via MCP (`get_project_url`/dashboard)
- [ ] Preencher `ANTHROPIC_API_KEY` no `.env` local para habilitar os agentes de IA
- [ ] Preencher `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` para habilitar notificações
- [ ] Confirmar criação do primeiro push para o GitHub remoto (repositório público)

## Curto prazo
- [ ] CI (GitHub Actions) rodando pytest com serviço Postgres
- [ ] CodeQL, Dependabot e Gitleaks configurados
- [ ] Popular `docs/architecture/plugins.md` rodando o Documentation Agent
- [ ] Popular `docs/database/schema.md` e `docs/agents/README.md`
