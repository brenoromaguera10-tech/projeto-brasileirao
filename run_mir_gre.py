from dashboard import build
ctx = {
  "slug":"fluminense-bragantino",
  "home":"Fluminense","away":"RB Bragantino",
  "home_key":"Fluminense","away_key":"Bragantino",
  "comp":"Brasileirão Série A · Rodada 19",
  "meta":"Maracanã, Rio de Janeiro · 17/07/2026 · 20:00",
  "odds_1x2":(1.90,3.40,4.33),
  "sub_1x2":"modelo 53% + mercado 50% = blend 52%",
  "sub_btts":"modelo 50% e mercado 50% — convergência total",
  "form_home":["?","?","?","?","?"],
  "form_away":["?","?","?","?","?"],
  "rating_home":"—","rating_away":"—",
  "ref":"Davi de Oliveira Lacerda","ref_yellow":"5,18","ref_red":"0,18",
  "ref_note":"(abaixo do juiz do Bahia; leve viés pró-under de cartões)",
  "cards":{
     "exp":"5,3",
     "sub":"árbitro Lacerda (5,18 am) — meu modelo fica ABAIXO do mercado: leve viés pró-under",
     "linhas":{
        "Over 3.5":(0.78,0.77),
        "Over 4.5":(0.65,0.61),
        "Over 5.5":(0.50,0.44),
        "Over 6.5":(0.35,0.28),
     }
  },
  "value":[
    {"mercado":"Vitória Fluminense (1x2)","odd":"1.90","precisa":"53%","estimo":"52%","veredito":"Justo"},
    {"mercado":"Empate","odd":"3.40","precisa":"29%","estimo":"27%","veredito":"-EV"},
    {"mercado":"Vitória Bragantino","odd":"4.33","precisa":"23%","estimo":"22%","veredito":"Justo"},
    {"mercado":"Ambos Marcam - Sim","odd":"1.90","precisa":"53%","estimo":"50%","veredito":"Justo"},
    {"mercado":"Over 2.5 gols","odd":"2.05","precisa":"49%","estimo":"45%","veredito":"-EV"},
    {"mercado":"Under 2.5 gols","odd":"1.75","precisa":"57%","estimo":"55%","veredito":"Justo"},
    {"mercado":"Under 5.5 cartões","odd":"1.83","precisa":"55%","estimo":"56%","veredito":"Valor"},
    {"mercado":"Over 5.5 cartões","odd":"1.83","precisa":"55%","estimo":"44%","veredito":"-EV"},
    {"mercado":"Over 4.5 cartões","odd":"1.44","precisa":"69%","estimo":"61%","veredito":"-EV"},
  ],
  "verdict":("ANÁLISE COMPLETA (times completos, jogo já rolando 0-0). Fluminense favorito moderado "
    "no Maracanã: blend modelo+mercado dá 52% (empate 27%, Bragantino 22%). BTTS e Over/Under batem "
    "no ponto com o mercado, inclinando levemente pro Under 2.5. A NOVIDADE são os cartões: com o "
    "árbitro Lacerda (5,18 amarelos/jogo, abaixo do juiz do Bahia), minha estimativa (~5,3) fica "
    "ABAIXO do que o mercado precifica (~5,5) — o único ponto do jogo com viés claro, levemente "
    "pró-UNDER de cartões. Under 5.5 @1.83 é a linha mais próxima de valor (est. 56% vs 55% de "
    "equilíbrio). No resto, mercado eficiente: jogo mais de leitura que de fichar."),
  "tips":[
    "Barras em degradê: vermelho = pouco provável, âmbar ≈ 50%, verde = muito provável.",
    "1x2, BTTS e Over/Under: modelo e mercado colados — leituras confiáveis, mas sem valor (odds justas).",
    "ÚNICO viés do jogo: cartões. O árbitro Lacerda é menos cartão que a média, então o mercado (~5,5) parece um fio alto → leve valor no UNDER 5.5.",
    "Cuidado: cartões ainda é confiança BAIXA (ancorado no árbitro, sem histórico por time). É um lean pequeno, não uma cravada.",
    "Resumo pra fichar: nenhuma aposta forte; se for buscar algo, Under 5.5 cartões é a única com 'Estimo' acima do 'Precisa'.",
  ],
}
print("OK:", build(ctx))
