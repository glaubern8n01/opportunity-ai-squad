# MEMORY

Histórico de sessões de trabalho no projeto. Entradas abaixo desta seção inicial são
anexadas automaticamente pelo Memory Agent ao final de cada `run` do squad
(`## Run `<id>` — <timestamp>`); a entrada abaixo é o registro manual da sessão de
bootstrap do projeto.

## Sessão de bootstrap — 2026-07-02

**Objetivo**: criar a fundação completa do Opportunity AI Squad a partir do zero
(diretório vazio), incluindo MCP do Supabase escopado ao projeto, ambiente Python,
arquitetura de plugins, schema do banco, os 17 agentes e documentação — tudo executado
diretamente pelo terminal, sem MVP descartável.

**O que foi feito**:
- Configurado `.mcp.json` (escopo de projeto) apontando para o Supabase novo
  (`kzokuvywgucvuasgbxgf`), separado do MCP global usado em outros projetos.
- Corrigida instalação do Supabase CLI (binário faltando via npm) reinstalando via scoop.
- Instalado `uv` (gerenciador Python) via scoop.
- Criado projeto Python com `uv init` + estrutura `src/opportunity_squad/` (Clean
  Architecture) e `plugins/` (plugin architecture com auto-discovery).
- Implementadas as interfaces do Core: `SourceConnector`, `AIProvider`, `Notifier`,
  `ReportGenerator`, `Agent` (todas em `core/interfaces/`).
- Implementado `plugins/registry.py` (discovery via `plugin.yaml` + `entry_point`).
- Implementados os plugins de exemplo: `github_trending` e `hacker_news` (fontes reais,
  sem autenticação, testados contra as APIs reais), `anthropic` (IA), `telegram`
  (notificação), `markdown` (relatório).
- Modelado o schema completo (21 tabelas) em SQLAlchemy 2.0 e gerada a migration
  inicial via Alembic — validada aplicando em Postgres local via Docker Compose.
- Implementados os 17 agentes (`agents/`) e o orquestrador (`scheduler/jobs.py` —
  `SquadOrchestrator` + APScheduler com pipelines de scan/report/mvp).
- Criado `main.py` (composition root) ligando config → plugins → agentes → scheduler.
- Escritos 18 testes automatizados (pytest) cobrindo scoring, config, plugin registry,
  conectores (mockados com `respx`) e agentes (Scout/Discovery, contra Postgres real).
  `ruff check` e `mypy` limpos.
- Testado end-to-end manualmente: Scout Agent descobriu 45 produtos reais (GitHub +
  Hacker News) e Discovery Agent qualificou 25 — dados de teste depois truncados.
- Criada documentação completa: README, ARCHITECTURE, ROADMAP, CHANGELOG, TODO,
  CONTRIBUTING, PROMPTS, SECURITY, LICENSE.

**Arquivos alterados**: praticamente todo o repositório (bootstrap inicial) — ver
`git log`/`git status` para o diff exato desta sessão.

**Problemas encontrados**:
- CLI do Supabase via `npm install -g supabase` vinha com o binário da plataforma
  ausente (`ENOENT`) → resolvido reinstalando via `scoop` (método oficial no Windows).
- `pydantic-settings` tentava fazer `json.loads` nos campos `list[str]` antes do
  `field_validator` rodar → resolvido anotando os campos com `NoDecode`.
- `ReportGenerator` não tinha `initialize()`, mas o `plugins.registry.load_plugin()`
  chama esse método em todo plugin carregado → adicionado `initialize()` no-op na
  interface, mantendo o mesmo ciclo de vida das outras três interfaces de plugin.
- `datetime.utcnow()`/`utcfromtimestamp()` estão deprecados no Python usado (3.13) →
  substituídos por `datetime.now(UTC)`/`datetime.fromtimestamp(x, UTC)` em todo o código.

**Soluções**: descritas acima, inline com cada problema.

**Decisões tomadas**:
- Agentes recebem plugins via injeção de construtor (não importam `plugins.registry`
  diretamente) — só `main.py` conhece o mecanismo de carregamento de plugins.
- `watchlist`/`favorites` usam um campo `owner` (string, default `"default"`) em vez de
  uma tabela de usuários — o sistema é single-tenant até que autenticação seja pedida.
- Reduzido o escopo de conectores implementados nesta sessão para 2 (github_trending,
  hacker_news) — cobrem os dois padrões de autenticação mais comuns (nenhuma e API
  key opcional) como referência; os ~40 conectores do briefing ficam no ROADMAP.md
  para implementação incremental, para não criar dezenas de pastas vazias sem valor.

**Próximos passos** (ver TODO.md/ROADMAP.md para detalhes):
1. Usuário concluir autenticação OAuth do MCP do Supabase (`claude /mcp`).
2. Obter a connection string do Supabase (via MCP `get_project_url`/dashboard) e
   aplicar `alembic upgrade head` no banco de produção.
3. Preencher `ANTHROPIC_API_KEY`/`TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` no `.env`.
4. Configurar GitHub Actions (CI, CodeQL, Dependabot, Gitleaks).
5. Confirmar com o usuário antes do primeiro `git push` para o repositório público.
