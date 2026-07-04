# Plugins instalados

_Gerado automaticamente pelo Documentation Agent._

## sources
- **github_trending** — Repositórios em alta via GitHub Search API oficial (busca por estrelas recentes). Não requer autenticação, mas aceita GITHUB_TOKEN opcional para rate limit maior.
- **hacker_news** — Posts (Show HN, top stories) via API oficial pública do Hacker News (Firebase). Não requer autenticação.
- **scrapegraph_ai** — Extração estruturada de páginas públicas via API hospedada da ScrapeGraphAI (SDK oficial scrapegraph-py). Combina busca na web com extração via LLM server-side — cobre fontes sem API oficial, sem scraping direto/agressivo. Requer SCRAPEGRAPH_API_KEY.

## ai
- **anthropic** — Provedor de IA via Anthropic API (Claude). Usa ANTHROPIC_MODEL_CHEAP para processamento em massa (Haiku), ANTHROPIC_MODEL para análises completas (Sonnet) e ANTHROPIC_MODEL_DEEP para análises profundas (Opus).

## notifications
- **telegram** — Envia oportunidades, relatórios, alertas e erros para um chat/canal do Telegram.

## reports
- **markdown** — Gera relatórios (diário/semanal/mensal) em Markdown, prontos para enviar via Telegram ou salvar em docs/reports/.

## exports
_Nenhum plugin implementado ainda._
