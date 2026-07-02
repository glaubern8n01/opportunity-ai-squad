# Política de Segurança

## Reportando uma vulnerabilidade

Este é um repositório público. Se você encontrar uma vulnerabilidade de segurança
(exposição de credenciais, injeção, falha de autenticação, RCE, etc.), **não abra uma
issue pública**. Em vez disso:

1. Envie um e-mail para **glaubermcorreia@gmail.com** com o assunto `[SECURITY] Opportunity AI Squad`.
2. Descreva o problema, passos para reproduzir e o impacto potencial.
3. Aguarde confirmação de recebimento em até 72 horas.
4. Um fix ou mitigação será priorizado antes de qualquer divulgação pública.

## Escopo

Considera-se vulnerabilidade de segurança neste projeto:

- Exposição de segredos (API keys, tokens, credenciais de banco) no código ou histórico do git.
- Falhas que permitam acesso não autorizado ao banco de dados (Supabase/PostgreSQL).
- Injeção de SQL, comandos ou prompt injection que leve a exfiltração de dados.
- Vulnerabilidades em dependências (`pyproject.toml`) com exploit conhecido.
- Bypass de validação de variáveis de ambiente obrigatórias.

## Boas práticas adotadas neste projeto

- Nenhum segredo é versionado — apenas `.env.example` com placeholders.
- `.gitignore` bloqueia `.env`, chaves, dumps de banco e credenciais.
- [Gitleaks](https://github.com/gitleaks/gitleaks) roda em CI para impedir commit acidental de segredos.
- [CodeQL](https://codeql.github.com/) analisa o código em busca de vulnerabilidades conhecidas.
- [Dependabot](https://docs.github.com/en/code-security/dependabot) mantém dependências atualizadas.
- Todas as variáveis obrigatórias são validadas na inicialização (`src/opportunity_squad/core/config.py`) — a aplicação falha rápido (fail-fast) se algo essencial estiver ausente.
- Conectores de fontes de dados respeitam APIs oficiais e Termos de Uso — sem scraping agressivo.
- No Supabase real, todas as tabelas têm RLS habilitado (padrão do projeto) e os grants
  CRUD padrão para `anon`/`authenticated` foram revogados explicitamente (schema
  `public`, incluindo `ALTER DEFAULT PRIVILEGES` para tabelas futuras) — o backend só é
  acessado via conexão Postgres direta (`DATABASE_URL`), nunca via PostgREST/Data API,
  então não há necessidade de policies de RLS granulares por usuário.

## Versões suportadas

Enquanto o projeto estiver em `0.x`, apenas a branch `main` recebe correções de segurança.

| Versão | Suportada |
| ------ | --------- |
| 0.x    | ✅        |
