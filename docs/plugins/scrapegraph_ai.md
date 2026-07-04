# Plugin de fonte: ScrapeGraphAI

Extração estruturada de páginas públicas via API hospedada da
[ScrapeGraphAI](https://scrapegraphai.com), usando o SDK oficial
[`scrapegraph-py`](https://github.com/ScrapeGraphAI/scrapegraph-py).

- Módulo: `plugins/sources/scrapegraph_ai/connector.py`
- Classe: `ScrapeGraphAIConnector`
- Categoria: `sources`
- Nome no `ENABLED_SOURCE_PLUGINS`: `scrapegraph_ai`

## Por que este SDK e não os outros

O projeto ScrapeGraphAI tem três formas de integração. Escolhemos o SDK oficial da
API hospedada (`scrapegraph-py`) e não as outras duas:

| Opção | O que é | Por que (não) foi usada |
| --- | --- | --- |
| `scrapegraph-py` (usado aqui) | SDK oficial da API hospedada — cliente HTTP fino (`httpx` + `pydantic`, sem mais nada) | Único que não exige infraestrutura própria: sem navegador, sem chave de LLM adicional, renderização e extração acontecem no servidor da ScrapeGraphAI |
| `scrapegraphai` (a lib `Scrapegraph-ai`) | Framework local que roda a pipeline de scraping (LLM + grafo) na sua própria máquina | Exige `playwright install` (Chromium local) **e** uma API key própria de LLM (OpenAI/Groq/Azure/Gemini) ou Ollama local — pesado demais para um plugin, e duplicaria a config de IA que o projeto já tem via `plugins/ai/anthropic` |
| `scrapegraph-mcp` | Servidor MCP (stdio/HTTP) que expõe as mesmas ferramentas para clientes MCP (Claude Desktop, Cursor, etc.) | É uma camada de integração para *assistentes* conversarem com a API, não uma biblioteca para embutir dentro de um backend Python — não se encaixa na `plugins.registry` (que carrega classes Python, não processos MCP) |

## Como funciona

Diferente de `github_trending`/`hacker_news` (que consomem uma API oficial já
estruturada de uma fonte fixa conhecida), este conector é **genérico**: não tem um
catálogo próprio de produtos, então:

- **`search(query)`** chama `client.search()` da ScrapeGraphAI, que faz uma busca na
  web e já retorna extração estruturada (via `prompt` + `schema` JSON Schema) dos
  resultados em uma única chamada. Se `query` for `None`, usa `default_query`
  (configurável) — um texto genérico buscando "novos produtos SaaS e ferramentas de
  IA lançados recentemente".
- **`fetch_details(external_id)`** trata `external_id` como a **própria URL** do
  produto (não um id nativo de uma fonte, já que não existe uma aqui) e chama
  `client.extract()` para essa URL específica. Por isso, `fetch_details` só funciona
  para itens cujo `external_id` comece com `http://`/`https://` — itens sem URL
  própria (fallback abaixo) não são "re-consultáveis".
- **`fetch_reviews(external_id)`** é melhor esforço: tenta extrair depoimentos da
  mesma página via `client.extract()` com um prompt diferente. Falhas retornam lista
  vazia em vez de propagar exceção, para não interromper o pipeline do Review Agent.
- **`normalize(raw)`** converte o item extraído (schema `products[]`, ver
  `_LIST_SCHEMA` no connector) em `NormalizedProduct`. Quando o item não tem `url`
  (pode acontecer em resultados de busca sem link claro), gera um `external_id`
  sintético determinístico (`sha256:<hash curto do nome>`) só para satisfazer a
  constraint `uq_products_source_external` — esses itens não suportam
  `fetch_details`/`fetch_reviews`.

## Configuração

```bash
# .env
SCRAPEGRAPH_API_KEY=sgai-...          # obrigatório para habilitar o plugin
ENABLED_SOURCE_PLUGINS=github_trending,hacker_news,scrapegraph_ai
```

A chave é obtida em <https://dashboard.scrapegraphai.com>. Sem
`SCRAPEGRAPH_API_KEY`, `plugins.registry.load_plugin` recusa carregar o plugin
(`requires_config: ["api_key"]` no `plugin.yaml`) com um erro claro — mesmo
comportamento de qualquer outro plugin com config obrigatória ausente.

Config interna opcional (definida em `main.py:_source_plugin_config`, não
exposta como env var própria hoje — ajustável no código se necessário):

- `default_query`: texto de busca usado quando `search(query=None)`.
- `num_results`: quantos resultados de busca pedir por chamada (default: 5).

## Limites e uso responsável

- Nenhuma requisição HTTP é feita diretamente a sites de terceiros pelo plugin — quem
  busca, renderiza e respeita `robots.txt`/rate limits é o serviço da ScrapeGraphAI.
- `search()`/`extract()` consomem créditos da conta ScrapeGraphAI (ver
  `client.credits()`, não exposto pelo plugin ainda). Evite chamar `search()` com
  `num_results` alto ou em loop apertado.
- Como qualquer fonte baseada em extração por LLM, o resultado é probabilístico —
  `Discovery Agent`/`Strategy Agent` já tratam produtos com dados incompletos, mas
  vale revisar amostras periodicamente.

## Testes

`tests/unit/test_scrapegraph_ai_connector.py` mockeia as chamadas HTTP (via `respx`,
mesmo padrão dos outros conectores) para `https://v2-api.scrapegraphai.com/api/{search,extract}`
— nenhum teste chama a API real nem precisa de uma chave válida.
