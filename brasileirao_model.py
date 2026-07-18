# Protocolo de retomada (qualquer sessão / aparelho)

Objetivo: retomar o projeto do zero em uma conversa nova.

## O que o Claude faz ao ouvir "continua o projeto Brasileirão"
1. `git clone <URL_DO_REPO>` — traz o motor completo (código + dados snapshot + modelo).
2. Reconecta no Supabase (conector MCP) do projeto do usuário.
3. Puxa o histórico atual: `select * from match_analyses order by analyzed_at desc`.
4. (Se houver dados novos de estatística) atualiza `stats_model.py` e regrava `team_stats`.
5. Pronto: análise + dashboard operando; cada novo jogo é inserido em `match_analyses` via MCP.

## Divisão de responsabilidades
- GitHub  = código + snapshot de dados + modelo treinado (fonte da verdade do MOTOR).
- Supabase = histórico crescente de análises e resultados (fonte da verdade dos DADOS/tracking).
- Sandbox Python NÃO acessa o Supabase direto; o Claude faz a ponte via MCP.

## Tabelas Supabase
team_stats · model_ratings · model_params · match_analyses
Projeto: brenoromaguera10@gmail.com's Project
