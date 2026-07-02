# Agentes

Todos implementam `core.interfaces.agent.Agent` (`run(context: AgentContext) ->
AgentResult`, nunca lança exceção). Dependências (plugins) são injetadas via
construtor em `main.py:build_agents`. Ver [ARCHITECTURE.md](../../ARCHITECTURE.md)
para o diagrama de camadas e [PROMPTS.md](../../PROMPTS.md) para os prompts de IA.

| Agente | Arquivo | IA? | O que faz |
| --- | --- | --- | --- |
| Scout | `scout_agent.py` | Não | Varre fontes habilitadas, faz upsert de produtos + snapshot em `product_versions` |
| Discovery | `discovery_agent.py` | Não | Pré-score heurístico a partir das métricas mais recentes, qualifica candidatos |
| Review | `review_agent.py` | Não | Busca reviews (`fetch_reviews`) dos produtos qualificados |
| Sentiment | `sentiment_agent.py` | Sim (Haiku) | Classifica sentimento das reviews sem rótulo |
| Trend | `trend_agent.py` | Não | Compara os 2 últimos snapshots, define direção de tendência e status do produto |
| Competitor | `competitor_agent.py` | Sim (Sonnet) | Levanta concorrentes diretos conhecidos |
| Market | `market_agent.py` | Sim (Sonnet) | Estima tamanho/crescimento de mercado |
| Gap | `gap_agent.py` | Sim (Sonnet) | Cruza reviews negativas recorrentes em ideias de melhoria |
| Strategy | `strategy_agent.py` | Sim (Sonnet) | Estima os 13 critérios e calcula o Opportunity Score final |
| MVP | `mvp_agent.py` | Sim (Opus) | Transforma ideias validadas em plano de MVP (stack + features) |
| Architecture | `architecture_agent.py` | Sim (Opus) | Gera roadmap técnico (milestones) para um MVP |
| Research | `research_agent.py` | Sim (Opus) | Pesquisa qualitativa profunda sob demanda (`context.data['product_id']`) |
| Report | `report_agent.py` | Não | Agrega dados do período e gera o relatório via plugin de report |
| Notification | `notification_agent.py` | Não | Entrega alertas pendentes e relatórios via plugin de notificação |
| Memory | `memory_agent.py` | Não | Registra o resultado de cada run e mantém `MEMORY.md` sincronizado |
| Security | `security_agent.py` | Não | Valida config obrigatória e varre por segredos óbvios |
| Documentation | `documentation_agent.py` | Não | Regenera `docs/architecture/plugins.md` a partir do plugin registry |

## Pipelines (`scheduler/jobs.py`)

- **`run_scan_pipeline`** (a cada `SCAN_INTERVAL_MINUTES`): scout → discovery → review →
  sentiment → trend → competitor → market → gap → strategy → security.
- **`run_report_pipeline`** (cron diário/semanal/mensal): report → notification.
- **`run_mvp_pipeline`** (a cada 6h): mvp → architecture.

Cada pipeline roda dentro de um `runs` row; o Memory Agent roda ao final de todo
`run_pipeline`, independente de sucesso/falha dos agentes anteriores.
