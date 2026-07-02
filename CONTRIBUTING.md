# Contribuindo

## Setup local

```bash
uv sync                        # instala dependências (Python 3.13+)
cp .env.example .env           # preencha com suas credenciais locais
docker compose up -d postgres  # banco local
uv run alembic upgrade head    # aplica migrations
uv run pytest                  # roda a suíte de testes
```

## Padrões de código

- **Lint/format**: `uv run ruff check .` (e `--fix` para autofix)
- **Types**: `uv run mypy src plugins`
- **Testes**: `uv run pytest` — `tests/unit` não depende de banco; `tests/integration`
  precisa do Postgres local rodando (`docker compose up -d postgres`)
- Sem comentários óbvios — só onde uma decisão não é evidente pelo código.
- Não adicione abstrações para casos hipotéticos; resolva o problema atual.

## Como criar um novo agente

1. Crie `src/opportunity_squad/agents/meu_agente.py` implementando
   `core.interfaces.agent.Agent` — método `execute(context: AgentContext) -> dict`.
2. Pode lançar exceção livremente: `run()` (herdado, não sobrescreva) já captura,
   loga e converte em `AgentResult(success=False, error=...)`. Só retorne o dict de
   output do agente — o `AgentResult` de sucesso é montado pela classe base.
3. Injete dependências (plugins) via `__init__`, nunca importe `plugins.registry` dentro do agente
   (exceção: introspecção read-only do catálogo de plugins, como faz `DocumentationAgent`).
4. Registre o agente em `src/opportunity_squad/agents/__init__.py` e monte-o em `main.py`.
5. Adicione-o a um pipeline em `scheduler/jobs.py` (`SquadOrchestrator`) se ele for
   parte de um fluxo agendado.

## Como criar um novo plugin (fonte, IA, notificação ou relatório)

1. Crie a pasta `plugins/<categoria>/<nome>/` com `__init__.py`, `plugin.yaml` e o
   módulo de implementação.
2. `plugin.yaml`:
   ```yaml
   name: meu_plugin
   category: sources   # sources | ai | notifications | reports | exports
   entry_point: "plugins.sources.meu_plugin.connector:MeuPluginConnector"
   description: "O que este plugin faz."
   requires_config: [api_key]   # chaves esperadas no dict de config
   ```
3. Implemente a interface correspondente de `core/interfaces/` (`SourceConnector`,
   `AIProvider`, `Notifier` ou `ReportGenerator`).
4. Adicione o nome do plugin em `ENABLED_*_PLUGINS` no `.env` — nada mais precisa mudar.
5. Escreva testes em `tests/unit/` (mock de rede com `respx` para fontes HTTP).

## Segurança

Nunca commite `.env`, chaves ou tokens. Veja [SECURITY.md](SECURITY.md) para como
reportar vulnerabilidades e quais checagens automáticas existem (Gitleaks, CodeQL,
Dependabot, Security Agent em runtime).

## Documentação

Ao concluir uma mudança relevante, atualize `CHANGELOG.md` e, se for uma decisão de
arquitetura ou progresso de sessão, `MEMORY.md`.
