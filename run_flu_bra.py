from dashboard import build
ctx = {
  "slug":"bahia-chapecoense",
  "home":"Bahia","away":"Chapecoense",
  "home_key":"Bahia","away_key":"Chapecoense",
  "comp":"Brasileirão Série A · Rodada 4",
  "meta":"Arena Fonte Nova, Salvador · 17/07/2026 · 19:30",
  "odds_1x2":(1.40,5.00,6.50),
  "form_home":["D","L","D","L","W"],
  "form_away":["L","D","L","L","L"],
  "rating_home":"6.84","rating_away":"6.68",
  "ref":"Paulo Cesar Zanovelli da Silva",
  "ref_yellow":"5,54","ref_red":"0,42",
  "ref_note":"(cartão acima da média da liga)",
  "cards":{
     "exp":"5",
     "linhas":{
        "Over 3.5":(0.69,0.75),
        "Over 4.5":(0.54,0.58),
        "Over 5.5":(0.37,0.40),
     }
  },
  "value":[
    {"mercado":"Vitória Bahia (1x2)","odd":"1.40","precisa":"71%","estimo":"70%","veredito":"Justo"},
    {"mercado":"Dupla: Bahia ou Empate","odd":"1.11","precisa":"90%","estimo":"88%","veredito":"Justo"},
    {"mercado":"Over 2.5 gols","odd":"1.60","precisa":"63%","estimo":"60%","veredito":"-EV"},
    {"mercado":"Ambos Marcam - Sim","odd":"1.80","precisa":"56%","estimo":"51%","veredito":"Sem valor"},
    {"mercado":"Ambos Marcam - Não","odd":"1.95","precisa":"51%","estimo":"49%","veredito":"Justo"},
    {"mercado":"Over 4.5 cartões","odd":"1.72","precisa":"58%","estimo":"58%","veredito":"Na trave"},
    {"mercado":"Over 5.5 cartões","odd":"2.50","precisa":"40%","estimo":"40%","veredito":"Na trave"},
    {"mercado":"Under 5.5 cartões","odd":"1.50","precisa":"67%","estimo":"62%","veredito":"-EV"},
  ],
  "verdict":("Favoritismo forte da Bahia em casa (70%), com os dois times completos e a Chapecoense "
    "em péssima fase (0 vitórias em 5). Expectativa de bastante gol (xG total 3.2) e ~5 cartões, "
    "com a Chape puxando a conta. Nas odds atuais nenhuma linha oferece vantagem clara — as mais "
    "próximas do justo são a vitória da Bahia e o 'ambos não'. O 1x2 é a leitura mais confiável; "
    "cartões, a menos confiável."),
  "tips":[
    "As barras seguem um degradê: vermelho = baixa probabilidade, âmbar = ~50%, verde = alta. Quanto mais verde e mais cheia, mais provável.",
    "Confie no selo de confiança: 1x2 (ALTA) empata com o mercado; Ambos Marcam (MÉDIA) teve convergência modelo×mercado; Cartões (BAIXA) é leitura de árbitro, sem histórico por time.",
    "'Precisa' vs 'Estimo' na tabela de valor: se 'Estimo' for MAIOR que 'Precisa', há valor na aposta; se for menor, a odd está cara.",
    "Nenhuma linha aqui tem 'Estimo' claramente acima de 'Precisa' — ou seja, é um jogo sem aposta de valor óbvio, mais pra leitura do que pra fichar.",
    "Cartões giram em torno de 5; a Chapecoense, correndo atrás e se defendendo, tende a ser o lado mais carimbado.",
    "Me mande o próximo jogo (e, se tiver, odds/escalação/árbitro) que o dashboard sai no mesmo formato.",
  ],
}
p = build(ctx)
print("OK:", p)
