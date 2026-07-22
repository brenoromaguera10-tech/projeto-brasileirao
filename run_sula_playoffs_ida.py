#!/usr/bin/env python3
"""Dashboards pré-análise v2 — Sula 2026, idas dos playoffs, 22/07/2026.
v2: campanhas completas FootyStats p/ times da Sula; Libertadores ainda parcial (wiki)."""
import math, sys
sys.path += [".", "leagues"]
from sula_campanha import analisar_sula
import dashboard

dashboard.get_model = lambda *a, **k: None
dashboard.analisar = lambda hk, ak, odds=None, model=None, texto=False: analisar_sula(hk, ak)

def pois_over(mean, line):
    """P(total > line) com total ~ Poisson(mean)."""
    k = int(math.floor(line))
    cdf = sum(math.exp(-mean)*mean**i/math.factorial(i) for i in range(k+1))
    return 1 - cdf

LIGA_CORNERS, LIGA_CARDS, LIGA_SHOTS = 4.52, 2.63, 13.1

def stats_block(shots_home, shots_away, ch, ca):
    ct = ch + ca
    return {"shots_home": shots_home, "shots_away": shots_away,
            "shots_total": shots_home+shots_away,
            "shots_home_1T": shots_home*0.44, "shots_away_1T": shots_away*0.44,
            "corners_home": ch, "corners_away": ca, "corners_total": ct,
            "over_corners_total": {f"{L}.5": pois_over(ct, L+0.5) for L in (7,8,9,10)}}

AVISO = ("PRÉ-ANÁLISE v2: campanha completa (FootyStats) para os times da Sula; Medellín/Lanús/Cristal "
         "ainda com base parcial da Libertadores. Sem odds — manda as da sua casa que eu fecho com blend 90% mercado.")

jogos = [
  dict(slug="sula-medellin-vasco",
       home="Ind. Medellín", away="Vasco da Gama",
       home_key="Independiente Medellin", away_key="Vasco da Gama",
       comp="Copa Sul-Americana · Playoffs · IDA",
       meta="Atanasio Girardot, Medellín · 22/07/2026 · 19:00 (volta no Rio, 28-30/07)",
       form_home=["V","E","D"], form_away=["V","V","V","E","D","D"],
       rating_home="3:5 em 3j (Libertadores, grupo c/ Flamengo)",
       rating_away="10:6 em 6j (7:2 em casa, 3:4 fora)",
       sub_1x2="campanha completa do Vasco virou o jogo: leve favorito ATÉ FORA de casa",
       sub_btts="ataques funcionam dos dois lados; defesa do DIM vazou 5 em 3",
       stats=stats_block(LIGA_SHOTS, 14.8, LIGA_CORNERS, 5.00),
       cards={"exp": "6,5", "sub": "Vasco toma MUITOS cartões (3,83/jogo, maior da amostra) + base 2,63 do adversário — jogo nervoso de mata-mata",
              "linhas": {}},
       tips=["v2 com FootyStats: Vasco leve favorito mesmo fora (39% x 35%) — defesa do DIM vazou 5 gols em 3 jogos de grupo.",
             "Ida sem prorrogação: empate leva a decisão pro Rio em boas condições pro Vasco.",
             "Cartões: Vasco médio de 3,83/jogo na Sula — linha alta de cartões merece atenção quando vier a odd.",
             AVISO],
       verdict=("VASCO LEVE FAVORITO ATÉ NO ATANASIO (39% fora · 26% empate · 35% casa, xG 1.27 x 1.36). "
                "A campanha completa mudou a leitura: ataque do Vasco fez 10 em 6 e a defesa do Medellín é o elo "
                "fraco (5 sofridos em 3). BTTS 53% é o número mais 'jogável' do confronto. Alerta de perfil: Vasco "
                "cartoleiro (3,83/jogo) em mata-mata continental fora de casa. Base do DIM ainda parcial — "
                "confiança BAIXA no 1x2, MÉDIA nos gols/escanteios. Manda as odds que eu fecho.")),
  dict(slug="sula-lanus-cienciano",
       home="Lanús", away="Cienciano",
       home_key="Lanus", away_key="Cienciano",
       comp="Copa Sul-Americana · Playoffs · IDA",
       meta="La Fortaleza, Lanús · 22/07/2026 · 21:30 (volta em Cusco — ALTITUDE 3.400m)",
       form_home=["V","V","D"], form_away=["V","V","E","E","E","D","D"],
       rating_home="2:1 em 3j (Libertadores)", rating_away="6:8 em 7j — SÓ 1 GOL em 3 jogos fora",
       sub_1x2="campanha completa derrubou o Cienciano: 1 gol marcado longe de Cusco",
       sub_btts="Cienciano fora: 1 marcado, 6 sofridos em 3 — BTTS improvável",
       stats=stats_block(LIGA_SHOTS, 14.0, LIGA_CORNERS, 3.86),
       cards={"exp": "4,1", "sub": "Cienciano limpo (1,43 cartão/jogo) e Lanús na base da liga — tendência UNDER cartões",
              "linhas": {}},
       tips=["A v2 derrubou o Cienciano: campanha completa é 6:8, com 1 gol marcado em 3 jogos FORA de Cusco.",
             "Lanús 52% e subindo se o mercado confirmar — a volta a 3.400m obriga o Lanús a definir HOJE; pressão real.",
             "Under 2.5 (modelo 75%) e Cienciano não marcar (xG 0.54) são as linhas mais interessantes pra conferir contra a odd.",
             AVISO],
       verdict=("LANÚS FAVORITO CLARO (52% · 31% · 17%, xG 1.17 x 0.54). O dado que decide: Cienciano marcou "
                "1 gol em 3 jogos longe da altitude de Cusco — e La Fortaleza fica ao nível do mar. Jogo de POUCOS "
                "gols (O2.5 só 25%) e POUCOS cartões (4,1 esperados; Cienciano é o time mais limpo da amostra). "
                "O Lanús precisa de margem hoje porque a volta a 3.400m é outra vida. Base do Lanús ainda parcial — "
                "1x2 confiança BAIXA-média; under gols/cartões é onde o dado é mais firme. Manda as odds.")),
  dict(slug="sula-cristal-bragantino",
       home="Sporting Cristal", away="RB Bragantino",
       home_key="Sporting Cristal", away_key="RB Bragantino",
       comp="Copa Sul-Americana · Playoffs · IDA",
       meta="Lima · 22/07/2026 · 21:30 (volta em Bragança Paulista, 28-30/07)",
       form_home=["V","V","D"], form_away=["V","V","V","E","D","D"],
       rating_home="4:2 em 3j (Libertadores, bateu Palmeiras)",
       rating_away="12:5 em 6j — 7:2 JOGANDO FORA",
       sub_1x2="v2 derrubou o exagero: de 59% para 42% — Bragantino é visitante perigoso",
       sub_btts="melhor ataque da noite (Bragantino 2/jogo) vs mando real do Cristal",
       stats=stats_block(LIGA_SHOTS, 19.2, LIGA_CORNERS, 5.33),
       cards={"exp": "5,3", "sub": "Bragantino disciplinado (2,67/jogo); jogo de cartões na média da liga",
              "linhas": {}},
       tips=["Correção da v1: com a campanha completa (12:5, 7:2 fora), o Bragantino subiu de 18% para 31% — o 59% do Cristal era artefato de amostra.",
             "Bragantino chuta 19,2 vezes/jogo (liga: 13,1) — volume ofensivo real; escanteios Over 9.5 é linha viva (52%).",
             "Cristal segue favorito pelo mando (venceu o Palmeiras em Lima), mas o jogo é muito mais aberto do que a v1 dizia.",
             AVISO],
       verdict=("JOGO ABERTO COM MANDO PESANDO (42% · 27% · 31%, xG 1.31 x 1.09). A v2 corrigiu a v1: o "
                "Bragantino da campanha real é o melhor ataque da noite (12 gols, 7 deles fora) e chuta 19/jogo. "
                "O mando do Cristal é legítimo (bateu o Palmeiras em Lima), mas 59% era exagero de amostra curta — "
                "o justo está na casa dos 40%. BTTS 48% e escanteios altos (9,9 esperados) são as linhas vivas. "
                "Base do Cristal ainda parcial — confiança BAIXA no 1x2, MÉDIA em gols/escanteios. Manda as odds.")),
]

for ctx in jogos:
    ctx.setdefault("value", [])
    path = dashboard.build(ctx, outdir="/home/claude")
    print("gerado:", path)
