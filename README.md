
# Projeto Brasileirão — Motor de Probabilidades

Sistema de análise de jogos da Série A: 1x2, Ambos Marcam, Gols, Chutes,
Escanteios e Cartões — com dashboard visual e comparação com o mercado.

## Arquivos
- brasileirao_model.py  — motor Dixon-Coles (gols): ratings de ataque/defesa,
  mando, peso por recência, calibração BTTS. Função fit()/predict().
- analise.py            — análise de um confronto (1x2, BTTS, over/under).
  Blend com o mercado calibrado por backtest: 85% mercado / 15% modelo.
- stats_model.py        — modelos de Chutes (nº2), Escanteios e Cartões (nº3)
  a partir de médias reais por time 2026 (chutes, escanteios for/against, faltas)
  + árbitro + amortecedor de competitividade nos cartões.
- dashboard.py          — gera o dashboard HTML (degradê de cor, selos de
  confiança, tabela de valor, dicas de leitura).
- run_*.py              — exemplos de geração de dashboard por jogo.
- modelo.pkl            — modelo treinado em cache.
- 477819a5-BRA.csv      — base histórica (gols+odds, 2012-2026).

## Uso rápido
    python3 analise.py "Fluminense" "Bragantino"
    # dashboard: ver run_flu_bra.py como modelo

## Dados persistidos no Supabase
Tabelas: team_stats, model_ratings, model_params, match_analyses.

## Regras do projeto
- Blend 1x2: 85% mercado / 15% modelo (calibrado por backtest).
- Divergência grande modelo x mercado = priorizar o mercado.
- Confiança por mercado sempre explícita (1x2 alta; gols/BTTS média;
  escanteios/chutes média; cartões menor).
- Nenhuma mudança no motor sem backtest (log-loss vs. mercado).
- Aposta é risco: o sistema apresenta probabilidades, não promessas.
