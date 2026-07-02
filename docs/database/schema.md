# Schema do banco de dados

PostgreSQL, modelado em SQLAlchemy 2.0 (`src/opportunity_squad/db/models/`), migrations
via Alembic (`alembic/versions/`). 21 tabelas de domínio + `alembic_version`.

| Tabela | Arquivo do modelo | Descrição |
| --- | --- | --- |
| `sources` | `db/models/source.py` | Fontes de dados cadastradas (product_hunt, reddit, github, ...) |
| `sources_logs` | `db/models/source.py` | Log de cada execução de fetch por fonte |
| `products` | `db/models/product.py` | Produtos/oportunidades rastreados |
| `product_versions` | `db/models/product.py` | Snapshot periódico de métricas (upvotes, downloads, usuários) |
| `reviews` | `db/models/review.py` | Reviews normalizadas, com sentimento (Sentiment Agent) |
| `competitors` | `db/models/competitor.py` | Concorrentes mapeados por produto (Competitor Agent) |
| `market_analysis` | `db/models/market.py` | Análise de mercado por produto/categoria (Market Agent) |
| `trend_analysis` | `db/models/market.py` | Direção/força de tendência (Trend Agent) |
| `analyses` | `db/models/analysis.py` | Análise qualitativa + Opportunity Score final (Strategy/Research Agent) |
| `reports` | `db/models/report.py` | Relatórios gerados (diário/semanal/mensal) |
| `alerts` | `db/models/report.py` | Alertas pendentes de entrega (Notification Agent) |
| `runs` | `db/models/ops.py` | Execuções do squad (uma por pipeline disparado) |
| `agent_logs` | `db/models/ops.py` | Logs estruturados por agente dentro de um run |
| `ideas` | `db/models/ideation.py` | Ideias de produto (originadas do Gap Agent ou manualmente) |
| `roadmaps` | `db/models/ideation.py` | Roadmap técnico de um MVP (Architecture Agent) |
| `mvp_projects` | `db/models/ideation.py` | Projetos de MVP derivados de ideias validadas (MVP Agent) |
| `features` | `db/models/ideation.py` | Features de um produto concorrente ou de um MVP próprio |
| `categories` | `db/models/taxonomy.py` | Categorias de produto (hierárquica via `parent_id`) |
| `tags` | `db/models/taxonomy.py` | Tags livres |
| `product_tags` | `db/models/taxonomy.py` | Associação N:N produtos↔tags |
| `watchlist` | `db/models/user.py` | Produtos marcados para acompanhamento (`owner` = single-tenant) |
| `favorites` | `db/models/user.py` | Produtos favoritados (`owner` = single-tenant) |

## Convenções

- Todas as tabelas usam `created_at`/`updated_at` (via `TimestampMixin`), exceto `runs`
  e `agent_logs` (têm seus próprios campos de tempo, mais adequados ao domínio).
- Nomes de constraints são determinísticos (`NAMING_CONVENTION` em `db/base.py`) para o
  Alembic gerar migrations consistentes entre bancos.
- Enums Python (`db/models/enums.py`) são persistidos como texto (`StrEnum`).

## Como gerar uma nova migration

```bash
# depois de alterar um model em db/models/
uv run alembic revision --autogenerate -m "descrição da mudança"
uv run alembic upgrade head
```

Revise sempre o arquivo gerado em `alembic/versions/` antes de commitar — o
autogenerate não detecta 100% das mudanças (ex.: renomear coluna vira DROP + ADD).
