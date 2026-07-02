# Reports

Pasta reservada para snapshots de relatórios gerados pelo `ReportAgent`
(`src/opportunity_squad/agents/report_agent.py`) quando exportados para arquivo —
hoje o conteúdo do relatório é persistido na tabela `reports` (ver
[docs/database/schema.md](../database/schema.md)), não em disco.

Se/quando um plugin de export para arquivo for adicionado (ex: PDF/HTML — ver
[ROADMAP.md](../../ROADMAP.md)), os artefatos gerados devem ser salvos aqui, nomeados
`<periodo>-<data>.<extensão>` (ex: `daily-2026-07-02.md`).
