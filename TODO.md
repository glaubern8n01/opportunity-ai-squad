# TODO

Itens técnicos de curto prazo. Para visão de produto/versões, ver [ROADMAP.md](ROADMAP.md).

## Bloqueado / aguardando o usuário
- [x] Concluir autenticação OAuth do MCP do Supabase (`claude /mcp` → selecionar `supabase`)
- [x] Aplicar a migration inicial no projeto Supabase real (`kzokuvywgucvuasgbxgf`) —
      aplicada via `mcp__supabase__apply_migration` em 2026-07-02 (22 tabelas, ver MEMORY.md)
- [ ] Preencher `DATABASE_URL` no `.env` com a connection string real do Supabase
      (senha do Postgres não é exposta pelo MCP por segurança — obter em
      Supabase Dashboard → Project Settings → Database → Connection string)
- [ ] Preencher `ANTHROPIC_API_KEY` no `.env` local para habilitar os agentes de IA
- [ ] Preencher `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` para habilitar notificações
- [ ] Confirmar criação do primeiro push para o GitHub remoto (repositório público)

## Curto prazo
- [x] CI (GitHub Actions) rodando pytest com serviço Postgres — `.github/workflows/ci.yml`
- [x] CodeQL, Dependabot e Gitleaks configurados — `.github/workflows/{codeql,gitleaks}.yml`, `.github/dependabot.yml`
- [x] Popular `docs/architecture/plugins.md` rodando o Documentation Agent
- [x] Popular `docs/database/schema.md` e `docs/agents/README.md`
- [x] Revogar grants CRUD padrão de `anon`/`authenticated` no Supabase real (RLS já
      habilitado por padrão, mas sem policies) — ver SECURITY.md
