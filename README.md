# Opportunity AI Squad

[![CI](https://github.com/glaubern8n01/opportunity-ai-squad/actions/workflows/ci.yml/badge.svg)](https://github.com/glaubern8n01/opportunity-ai-squad/actions/workflows/ci.yml)
[![CodeQL](https://github.com/glaubern8n01/opportunity-ai-squad/actions/workflows/codeql.yml/badge.svg)](https://github.com/glaubern8n01/opportunity-ai-squad/actions/workflows/codeql.yml)
[![Gitleaks](https://github.com/glaubern8n01/opportunity-ai-squad/actions/workflows/gitleaks.yml/badge.svg)](https://github.com/glaubern8n01/opportunity-ai-squad/actions/workflows/gitleaks.yml)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Esquadrão de agentes de IA que trabalha continuamente descobrindo oportunidades de
apps, SaaS, startups e negócios digitais: pesquisa produtos em crescimento, analisa
reviews, tendências, concorrentes e gaps de mercado, e gera relatórios com um
**Opportunity Score (0-10)** — tudo enviado automaticamente via Telegram.

Não é um MVP descartável: a arquitetura nasceu para produção — Clean Architecture,
plugins com auto-discovery, schema completo, testes e CI desde o primeiro commit.

## Índice

- [Objetivo](#objetivo)
- [Arquitetura](#arquitetura)
- [Fluxo](#fluxo)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Instalação](#instalação)
- [Docker / Docker Compose](#docker--docker-compose)
- [Banco de dados (PostgreSQL / Supabase)](#banco-de-dados-postgresql--supabase)
- [Anthropic (IA)](#anthropic-ia)
- [Telegram](#telegram)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Como criar um novo agente](#como-criar-um-novo-agente)
- [Como criar uma nova fonte (plugin)](#como-criar-uma-nova-fonte-plugin)
- [Como contribuir](#como-contribuir)
- [Deploy no EasyPanel](#deploy-no-easypanel)
- [Roadmap](#roadmap)
- [FAQ](#faq)
- [Licença](#licença)

## Objetivo

Descobrir automaticamente oportunidades de produto (apps, SaaS, ferramentas de IA,
startups) analisando lançamentos, reviews, tendências e concorrência em dezenas de
fontes públicas — e transformar isso em relatórios acionáveis e, quando validado, em
planos de MVP prontos para execução.

## Arquitetura

Clean Architecture + Plugin Architecture (SOLID, com ênfase em DIP/OCP). Ver o
detalhamento completo em [ARCHITECTURE.md](ARCHITECTURE.md).

```
main.py (composition root)
   └── agents/ (17 agentes — dependem só de core/interfaces/)
          └── core/interfaces/ (SourceConnector, AIProvider, Notifier, ReportGenerator, Agent)
                 ▲
                 └── plugins/ (sources, ai, notifications, reports, exports — auto-discovery)
   └── db/ (SQLAlchemy + Alembic, PostgreSQL/Supabase)
```

## Fluxo

```
Scout → Discovery → Review → Sentiment → Trend → Competitor → Market → Gap → Strategy
                                                                              │
                                                        Opportunity Score (0-10)
                                                                              │
                                              Report → Notification (Telegram)
                                                                              │
                                        (ideias validadas) → MVP → Architecture
```

Agendado via APScheduler (`scheduler/jobs.py`): scan a cada `SCAN_INTERVAL_MINUTES`,
relatórios diário/semanal/mensal, e pipeline de MVP a cada 6h.

## Estrutura do repositório

```
src/opportunity_squad/
├── agents/          # os 17 agentes do squad
├── core/            # interfaces, config, entidades de domínio, logging
├── db/              # models SQLAlchemy + sessão
├── scheduler/        # orquestrador de pipelines + APScheduler
├── scoring/          # Opportunity Score
├── api/              # FastAPI (healthcheck, catálogo de plugins)
└── main.py            # composition root

plugins/               # fontes, IA, notificações, relatórios — auto-discovery
alembic/                # migrations
docs/                   # agents, architecture, database, reports, research, prompts
tests/                  # unit (sem banco) + integration (Postgres real)
```

## Instalação

Requer Python 3.13+, [uv](https://docs.astral.sh/uv/), Docker e Docker Compose.

```bash
git clone https://github.com/glaubern8n01/opportunity-ai-squad.git
cd opportunity-ai-squad
uv sync                        # instala todas as dependências
cp .env.example .env           # preencha com suas credenciais
docker compose up -d postgres  # banco local
uv run alembic upgrade head    # aplica as migrations
uv run pytest                  # roda a suíte de testes
uv run python -m opportunity_squad.main   # inicia o scheduler
```

## Docker / Docker Compose

```bash
docker compose up -d --build   # sobe postgres + app
docker compose logs -f app
```

O `docker/Dockerfile` é multi-stage e usa `uv` para builds reprodutíveis e rápidos.

## Banco de dados (PostgreSQL / Supabase)

O schema tem 21 tabelas (produtos, reviews, análises, relatórios, ideias, MVPs...) —
ver [docs/database/schema.md](docs/database/schema.md). Migrations com Alembic:

```bash
uv run alembic revision --autogenerate -m "descrição"
uv run alembic upgrade head
```

Em produção, `DATABASE_URL` aponta para um projeto [Supabase](https://supabase.com/)
dedicado a este squad (use a connection string do **pooler**, porta `6543`). O MCP do
Supabase está configurado no escopo deste projeto (`.mcp.json`) para uso com Claude Code.

## Anthropic (IA)

```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-5          # análises completas
ANTHROPIC_MODEL_CHEAP=claude-haiku-4-5   # processamento em massa (ex: sentimento)
ANTHROPIC_MODEL_DEEP=claude-opus-4-8     # análises profundas (MVP, arquitetura, pesquisa)
```

Ver [PROMPTS.md](PROMPTS.md) para os prompts de sistema usados por cada agente.

## Telegram

1. Crie um bot com o [@BotFather](https://t.me/BotFather) e copie o token.
2. Pegue o `chat_id` (envie uma mensagem ao bot e consulte
   `https://api.telegram.org/bot<TOKEN>/getUpdates`).
3. Preencha no `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=123456:ABC-...
   TELEGRAM_CHAT_ID=123456789
   ENABLED_NOTIFICATION_PLUGINS=telegram
   ```

## Variáveis de ambiente

Ver [.env.example](.env.example) para a lista completa e comentada. Todas as variáveis
obrigatórias são validadas na inicialização (`core/config.py`) — a aplicação falha
rápido se algo essencial estiver faltando.

## Como criar um novo agente

Ver [CONTRIBUTING.md](CONTRIBUTING.md#como-criar-um-novo-agente) — resumo: implemente
`core.interfaces.agent.Agent`, injete plugins via construtor, registre em
`agents/__init__.py` e `main.py`, adicione a um pipeline em `scheduler/jobs.py`.

## Como criar uma nova fonte (plugin)

Ver [CONTRIBUTING.md](CONTRIBUTING.md#como-criar-um-novo-plugin-fonte-ia-notificação-ou-relatório)
— resumo: crie `plugins/sources/<nome>/` com `plugin.yaml` + implementação de
`SourceConnector`, adicione o nome em `ENABLED_SOURCE_PLUGINS`. Nenhuma mudança no Core.

Fontes atuais: `github_trending` e `hacker_news` (APIs oficiais sem autenticação) e
`scrapegraph_ai` (extração estruturada de páginas públicas sem API oficial própria,
via API hospedada da ScrapeGraphAI — requer `SCRAPEGRAPH_API_KEY`; ver
[docs/plugins/scrapegraph_ai.md](docs/plugins/scrapegraph_ai.md)).

## Como contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md).

## Deploy no EasyPanel

1. Crie um novo serviço "App" apontando para este repositório, build via Dockerfile
   (`docker/Dockerfile`).
2. Configure as variáveis de ambiente do `.env.example` na aba de Environment do EasyPanel
   (nunca commite o `.env` — preencha direto na UI do EasyPanel).
3. Se não usar Supabase, adicione um serviço PostgreSQL gerenciado pelo EasyPanel e aponte
   `DATABASE_URL` para ele.
4. Configure healthcheck apontando para o processo do `main.py` (scheduler) ou, se expor a
   API, para `GET /health` (porta padrão do Uvicorn, 8000).
5. Ative restart automático — o scheduler roda em processo único e de longa duração.

## Roadmap

Ver [ROADMAP.md](ROADMAP.md).

## FAQ

**Preciso rodar tudo com Docker?**
Não — `uv sync` + Postgres (local ou Supabase) + `uv run python -m opportunity_squad.main`
funciona sem Docker. O Compose é uma conveniência para o Postgres local.

**Como desabilito um plugin?**
Remova o nome da variável `ENABLED_*_PLUGINS` correspondente no `.env`. Nenhum código muda.

**Os agentes de IA quebram o app se `ANTHROPIC_API_KEY` não estiver configurada?**
Não — `main.py` detecta a ausência e desabilita apenas os agentes que dependem de IA,
mantendo Scout/Discovery/Review/Trend/Security/Memory/Documentation funcionando.

## Licença

[MIT](LICENSE).
