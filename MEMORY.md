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

## Sessão de revisão final pré-push — 2026-07-02

**Objetivo**: revisão estrutural completa (arquitetura, duplicação, segurança,
documentação, organização de pastas) antes do primeiro push para o repositório
público, a pedido do usuário.

**O que foi feito**:
- Instalado e rodado `gitleaks detect` real sobre o histórico do git (além do grep
  manual por padrões de segredo) — nenhum leak encontrado.
- Confirmado via `grep`/análise estática que `core/` e `agents/` nunca importam
  `plugins/` diretamente (exceto `DocumentationAgent`/`api/app.py`, que fazem apenas
  introspecção read-only do catálogo, não uso de lógica de um plugin específico) e
  que `plugins/` nunca importa `agents/`/`scheduler/` — direção de dependência (DIP)
  íntegra.
- Refatorado `core/interfaces/agent.py`: `Agent.run()` virou um template method que
  centraliza o try/except e o log de sucesso/falha; os 17 agentes agora implementam
  `execute(context) -> dict` e podem lançar livremente. Removeu ~75 linhas de
  boilerplate idêntico duplicado em todos os agentes.
- `ReportAgent` não colocava mais o conteúdo do relatório no `AgentResult.output`
  (era gerado mas nunca consumido — `NotificationAgent` já busca via `report_id` no
  banco) — removido por ser dado morto.
- `plugins/registry.py::load_plugin()` passou a validar `manifest.requires_config`
  antes de instanciar o plugin, com erro claro (`PluginLoadError`) em vez de deixar
  cada plugin descobrir isso sozinho dentro de `initialize()`. Antes, esse campo do
  `plugin.yaml` era só documentação, nunca era checado.
- Corrigida imprecisão na documentação: `main.py`, `ARCHITECTURE.md`,
  `docs/agents/README.md` e `CONTRIBUTING.md` diziam que `main.py` era o "único
  lugar" que conhece `plugins.registry`, mas isso já não era verdade
  (`DocumentationAgent`/`api/app.py` também o fazem, por razões legítimas).
- `docs/reports/`, `docs/research/`, `docs/prompts/` existiam no disco mas, por
  estarem vazias, não eram rastreadas pelo git (git não versiona diretórios vazios)
  — ficariam ausentes no primeiro push. Adicionado um `README.md` explicativo em
  cada uma.
- Reforçado `.gitignore` (`.pgpass`, `*.tmp`, `*.bak`, `Desktop.ini`).
- Suíte re-executada do zero após todas as mudanças: 19/19 testes, `ruff` e `mypy`
  limpos, migration reaplicada localmente sem erro.

**Arquivos alterados**: `core/interfaces/agent.py`, os 17 arquivos em `agents/`,
`plugins/registry.py`, `main.py`, `.gitignore`, `ARCHITECTURE.md`, `CONTRIBUTING.md`,
`docs/agents/README.md`, `CHANGELOG.md`, `tests/unit/test_registry.py`, e três novos
`docs/{reports,research,prompts}/README.md`.

**Problemas encontrados**: nenhum bug funcional novo — os achados foram todos de
qualidade/manutenibilidade (duplicação, metadado não utilizado, docs desatualizadas,
pastas vazias fora do git), não de correção.

**Decisões tomadas**:
- Não extraí um helper para o padrão `json.loads(response)` com fallback (repetido
  em 7 agentes de IA) — é só 4-5 linhas por agente e a mensagem de warning varia por
  contexto; extrair criaria uma abstração para economizar pouco, então mantive
  inline em cada agente.
- Mantive `DocumentationAgent`/`api/app.py` importando `plugins.registry`
  diretamente em vez de criar uma interface só para introspecção — são os únicos
  dois casos, ambos read-only, e uma interface para isso seria abstração prematura.

**Próximos passos**: aguardando o usuário concluir a autenticação OAuth do MCP do
Supabase para aplicar a migration no banco real; aguardando aprovação explícita do
usuário para o primeiro `git push`.

## Sessão de aplicação da migration no banco real — 2026-07-02

**Objetivo**: com o MCP do Supabase já autenticado pelo usuário, validar a conexão e
aplicar a migration inicial no projeto Supabase real (`kzokuvywgucvuasgbxgf`).

**O que foi feito**:
- Validada a conexão via `mcp__supabase__get_project_url` (`https://kzokuvywgucvuasgbxgf.supabase.co`)
  e `mcp__supabase__list_tables` (banco vazio antes da migration, confirmando que era
  a primeira aplicação).
- Em vez de transcrever o SQL manualmente a partir da migration do Alembic (risco de
  erro), gerado o DDL exato rodando `alembic upgrade head --sql` (modo offline, já
  suportado por `alembic/env.py` — não precisa de conexão real, só lê a URL do `.env`).
- Aplicado o DDL limpo (sem as linhas de log do Alembic, mantendo `BEGIN`/`COMMIT`
  implícitos no `apply_migration`) via `mcp__supabase__apply_migration`, incluindo a
  tabela `alembic_version` e o `INSERT` da revision `734d10e8f4c9` — assim, se o
  `DATABASE_URL` do `.env` for apontado para o Postgres real do Supabase no futuro,
  `alembic upgrade head` vai reconhecer a migration como já aplicada em vez de tentar
  recriar as tabelas.
- Confirmadas as 22 tabelas (21 do schema + `alembic_version`) via `list_tables` e
  checado `get_advisors(type="security")` pós-migration.

**Problemas encontrados**:
- O projeto Supabase tem uma função `rls_auto_enable()` (`SECURITY DEFINER`) que
  habilita RLS automaticamente em toda tabela nova, sem criar policies — todas as 22
  tabelas ficaram com `rls_enabled: true` e zero policies. Não bloqueia o app (que
  acessa via SQLAlchemy/psycopg direto com a connection string, não via PostgREST/
  `anon`/`authenticated`), mas é relevante caso a API REST do Supabase seja exposta
  no futuro — nesse caso as policies precisarão ser criadas explicitamente.
- O MCP do Supabase não expõe a senha do Postgres (por design/segurança) — não foi
  possível montar automaticamente a connection string completa para popular
  `DATABASE_URL` no `.env`. Isso ainda depende do usuário pegar a connection string
  no dashboard (Project Settings → Database).

**Decisões tomadas**:
- Preferido gerar o SQL via `alembic upgrade head --sql` em vez de escrever/copiar o
  DDL manualmente a partir do arquivo de migration — garante fidelidade byte-a-byte
  com o que `alembic upgrade head` geraria localmente, e mantém as duas fontes
  (Alembic local + Supabase real) em sync via a linha `INSERT INTO alembic_version`.

**Próximos passos**: usuário preencher `DATABASE_URL` (via dashboard do Supabase),
`ANTHROPIC_API_KEY` e tokens do Telegram no `.env`; decidir se/quando criar policies
de RLS; aprovar o primeiro `git push` para o repositório público.

**Nota de fechamento desta sessão**: ao revisar TODO.md, os itens de "curto prazo"
(CI, CodeQL, Dependabot, Gitleaks, docs populados) já estavam implementados no
repositório — o TODO.md estava desatualizado, não o trabalho em si. Corrigido nesta
sessão. O único item de fato pendente era o hardening de grants no Supabase real
(abaixo).

## Sessão de hardening de RLS/grants no Supabase real — 2026-07-02

**Objetivo**: a pedido do usuário, endurecer o acesso ao banco Supabase real após a
migration inicial — RLS já vinha habilitado automaticamente pelo projeto (função
`rls_auto_enable()`), mas sem policies.

**O que foi feito**:
- Checado `information_schema.role_table_grants` para a tabela `products` e confirmado
  que `anon`/`authenticated` tinham grants CRUD completos (SELECT/INSERT/UPDATE/DELETE/
  TRUNCATE/REFERENCES/TRIGGER) em todas as 22 tabelas — comportamento padrão do
  Supabase para o schema `public`.
- Aplicada uma segunda migration via `mcp__supabase__apply_migration`
  (`revoke_anon_authenticated_grants`): `REVOKE ALL` em todas as tabelas/sequences/
  functions do schema `public` de `anon`/`authenticated`, mais `ALTER DEFAULT
  PRIVILEGES` para que tabelas futuras já nasçam sem esses grants.
- Confirmado com uma nova query a `role_table_grants` que a lista ficou vazia para
  `anon`/`authenticated` no schema `public`.
- Documentada a decisão em SECURITY.md.

**Decisões tomadas**:
- Não foram criadas policies de RLS por linha/usuário — este backend nunca é acessado
  via PostgREST/Data API do Supabase (só via `DATABASE_URL`/SQLAlchemy direto), então
  não existe um conceito de "usuário autenticado via Supabase Auth" que precise de
  policies granulares. RLS habilitado + zero grants para `anon`/`authenticated` é a
  postura correta aqui; policies granulares ficam para se/quando o projeto expuser a
  Data API do Supabase diretamente a clientes.

**Próximos passos**: mesmos de antes (preencher `.env`, aprovar push) — nada novo
bloqueado por esta sessão.

## Sessão: ANTHROPIC_API_KEY preenchida e plugin ScrapeGraphAI adicionado — 2026-07-03

**Objetivo**: (1) preencher `ANTHROPIC_API_KEY` real no `.env` local a pedido do
usuário; (2) pesquisar e instalar suporte ao ScrapeGraphAI como novo plugin de fonte,
seguindo a arquitetura de plugins existente.

**O que foi feito**:
- `ANTHROPIC_API_KEY` preenchida em `.env` (fora do git) e validada com uma chamada
  real à API (`claude-haiku-4-5-20251001`, custo mínimo) — funcionando.
- Pesquisados os três repositórios do ScrapeGraphAI (`Scrapegraph-ai`, `scrapegraph-py`,
  `scrapegraph-mcp`) e escolhido `scrapegraph-py` (SDK oficial da API hospedada):
  única opção sem infraestrutura própria (sem Playwright/Chromium, sem API key de LLM
  adicional) — a lib local (`scrapegraphai`) exigiria isso, e o `scrapegraph-mcp` é
  para clientes MCP (Claude Desktop etc.), não para embutir num backend Python.
  Detalhes da decisão em [docs/plugins/scrapegraph_ai.md](docs/plugins/scrapegraph_ai.md).
- Instalado via `uv add scrapegraph-py` (v2.1.0, deps mínimas: `httpx`+`pydantic`,
  já usadas no projeto) — `pyproject.toml` atualizado automaticamente.
- Inspecionado o código-fonte real instalado (`.venv/.../scrapegraph_py/`) em vez de
  confiar só na doc do GitHub, para pegar a assinatura exata de `client.search()`/
  `client.extract()` e o formato de `ApiResult`/`ExtractResponse`/`SearchResponse`.
- Criado o plugin `plugins/sources/scrapegraph_ai/` (`connector.py` + `plugin.yaml`,
  `requires_config: ["api_key"]`): como a ScrapeGraphAI não tem catálogo próprio de
  produtos (diferente de `github_trending`/`hacker_news`), `search()` usa
  `client.search()` (busca na web + extração via schema em uma chamada) e
  `fetch_details(external_id)` trata `external_id` como a própria URL do produto,
  chamando `client.extract()` nela. `fetch_reviews()` é melhor esforço (retorna `[]`
  em vez de propagar erro se a página não tiver depoimentos extraíveis).
- Adicionada `scrapegraph_api_key: str | None` em `core/config.py`
  (`SCRAPEGRAPH_API_KEY`) e wireado em `main.py:_source_plugin_config`.
- Atualizado `.env.example` (nunca o `.env` real) com `SCRAPEGRAPH_API_KEY=` e
  comentário apontando para o dashboard da ScrapeGraphAI.
- Escritos 7 testes (`tests/unit/test_scrapegraph_ai_connector.py`, mockando
  `https://v2-api.scrapegraphai.com/api/{search,extract}` via `respx`, mesmo padrão
  dos outros conectores) cobrindo: normalização de resultados de busca, query
  default, `fetch_details` por URL, rejeição de `external_id` que não é URL,
  `fetch_reviews` melhor-esforço e o fallback de id sintético sem URL.
- `docs/plugins/scrapegraph_ai.md` criado (novo tipo de doc — deep-dive por plugin,
  além do `docs/architecture/plugins.md` gerado automaticamente); rodado o
  Documentation Agent manualmente para regenerar `docs/architecture/plugins.md`
  (agora lista 6 plugins) em vez de editar esse arquivo à mão.
- `README.md`/`ARCHITECTURE.md`/`CHANGELOG.md`/`ROADMAP.md` atualizados.
- `ruff check .` limpo, `mypy src plugins` limpo, suíte completa: 26/26 testes
  passando (19 anteriores + 7 novos).

**Decisões tomadas**:
- SDK hospedado (`scrapegraph-py`) em vez da lib local ou do MCP server — ver tabela
  comparativa em `docs/plugins/scrapegraph_ai.md`.
- `external_id` deste plugin é a própria URL do item (não um id nativo de fonte),
  porque ScrapeGraphAI não tem conceito de "id" — isso é uma exceção documentada ao
  padrão dos outros conectores (que usam ids nativos da fonte, ex. `full_name` do
  GitHub, `id` do HN).
- `fetch_reviews` engole exceções e retorna `[]` em vez de propagar — decisão
  deliberada porque nem toda página tem depoimentos extraíveis, e isso não deve
  quebrar o pipeline do Review Agent (diferente de `search`/`fetch_details`, que
  propagam erro via `SourceFetchError` normalmente, com retry).

**Próximos passos**: usuário preencher `SCRAPEGRAPH_API_KEY` real (opcional, só se for
habilitar o plugin em `ENABLED_SOURCE_PLUGINS`); considerar expor `default_query`/
`num_results` como env vars próprias se o uso em produção pedir ajuste sem redeploy.
