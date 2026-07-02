# Arquitetura

## Princípios

- **Clean Architecture**: o domínio (`core/`, `agents/`) nunca depende de detalhes de
  infraestrutura (SDKs, HTTP, banco). Ele depende apenas de interfaces (`core/interfaces/`).
- **SOLID**, com ênfase em **DIP** (Dependency Inversion) e **OCP** (Open/Closed):
  novos plugins são adicionados sem alterar o Core.
- **Plugin Architecture com Auto Discovery**: qualquer fonte, provedor de IA, canal de
  notificação ou formato de relatório é um plugin independente, habilitado via `.env`.

## Camadas

```
┌─────────────────────────────────────────────────────────────────┐
│  main.py (composition root)                                     │
│  — único lugar que carrega plugins para USO nos agentes.         │
│    (DocumentationAgent e api/app.py só fazem introspecção        │
│    read-only do registry, sem depender de lógica de um plugin)   │
└───────────────────────────┬─────────────────────────────────────┘
                             │ injeta instâncias de plugins nos agentes
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  agents/  (domínio da aplicação)                                 │
│  ScoutAgent, DiscoveryAgent, ReviewAgent, SentimentAgent,        │
│  TrendAgent, CompetitorAgent, MarketAgent, GapAgent,             │
│  StrategyAgent, MvpAgent, ArchitectureAgent, ResearchAgent,      │
│  ReportAgent, NotificationAgent, MemoryAgent, SecurityAgent,     │
│  DocumentationAgent                                              │
│  — dependem apenas de core.interfaces.*, nunca de um plugin      │
│    concreto                                                      │
└───────────────────────────┬─────────────────────────────────────┘
                             │ implementa
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  core/interfaces/  (contratos / portas)                          │
│  SourceConnector · AIProvider · Notifier · ReportGenerator · Agent│
└───────────────────────────┬─────────────────────────────────────┘
                             ▲ implementa
                             │
┌─────────────────────────────────────────────────────────────────┐
│  plugins/  (infraestrutura, auto-discovery via plugin.yaml)      │
│  sources/{github_trending,hacker_news,...}                       │
│  ai/{anthropic,...}  notifications/{telegram,...}                │
│  reports/{markdown,...}  exports/{...}                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  db/  (persistência)                                              │
│  SQLAlchemy models + Alembic migrations, PostgreSQL (Supabase)   │
└─────────────────────────────────────────────────────────────────┘
```

`scheduler/jobs.py` contém o `SquadOrchestrator`, que executa pipelines de agentes
(`run_scan_pipeline`, `run_report_pipeline`, `run_mvp_pipeline`) e os agenda via
APScheduler. Cada execução completa vira uma linha em `runs`, com o resultado de
cada agente registrado por `agent_logs`/`MemoryAgent`.

## Sistema de plugins

Cada plugin fica em `plugins/<categoria>/<nome>/` com:

```
plugins/sources/minha_fonte/
├── __init__.py
├── plugin.yaml       # manifesto: name, category, entry_point, requires_config
└── connector.py       # implementa core.interfaces.source.SourceConnector
```

`plugins/registry.py` descobre manifestos (`discover()`), importa a classe do
`entry_point` (`modulo.pontilhado:Classe`) e a instancia/inicializa (`load_plugin()`).
Habilitar um plugin é só adicionar o nome em `ENABLED_SOURCE_PLUGINS` (ou
`ENABLED_AI_PLUGINS`/`ENABLED_NOTIFICATION_PLUGINS`/`ENABLED_REPORT_PLUGINS`) no `.env`
— nenhum código muda. Ver [docs/architecture/plugins.md](docs/architecture/plugins.md)
para a lista atual (gerada automaticamente pelo Documentation Agent).

## Banco de dados

21 tabelas (ver [docs/database/schema.md](docs/database/schema.md)), migrations com
Alembic (`alembic/versions/`), rodando sobre PostgreSQL — em produção, o projeto
Supabase dedicado deste squad.

## Opportunity Score

`scoring/opportunity_score.py` calcula a nota final (0-10) como uma média ponderada de
13 critérios (mercado, concorrência, receita estimada, reviews, usuários/downloads,
tendência, facilidade de desenvolver, potencial de IA, potencial de automação,
escalabilidade, complexidade, chance de monetização, chance de viralização). O
`StrategyAgent` estima esses critérios via IA e persiste o resultado em `analyses`.
