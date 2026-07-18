from dashboard import build
ctx = {
  "slug":"mirassol-gremio",
  "home":"Mirassol","away":"Grêmio",
  "home_key":"Mirassol","away_key":"Gremio",
  "comp":"Brasileirão Série A · Rodada 19",
  "meta":"Estádio Maião, Mirassol · 17/07/2026 · 20:00",
  "odds_1x2":(2.05,3.10,4.00),
  "stats":__import__("stats_model").estimate("Mirassol","Gremio"),
  "sub_1x2":"blend corrigido 85% mercado / 15% modelo → 47% (era 50% no 50/50 antigo)",
  "sub_btts":"modelo 51% x mercado 44% — modelo mais aberto",
  "form_home":["?","?","?","?","?"],
  "form_away":["?","?","?","?","?"],
  "rating_home":"—","rating_away":"—",
  "ref":"não informado","ref_yellow":"—","ref_red":"—",
  "ref_note":"(mande o árbitro p/ cartões)",
  "cards":{"exp":"—","sub":"aguardando árbitro e odds de cartão","linhas":{}},
  "value":[
    {"mercado":"Vitória Mirassol (1x2)","odd":"2.05","precisa":"49%","estimo":"50%","veredito":"Cautela"},
    {"mercado":"Empate","odd":"3.10","precisa":"32%","estimo":"27%","veredito":"-EV"},
    {"mercado":"Vitória Grêmio","odd":"4.00","precisa":"25%","estimo":"23%","veredito":"Justo"},
    {"mercado":"Ambos Marcam - Sim","odd":"2.10","precisa":"48%","estimo":"48%","veredito":"Justo"},
    {"mercado":"Ambos Marcam - Não","odd":"1.66","precisa":"60%","estimo":"52%","veredito":"-EV"},
    {"mercado":"Over 2.5 gols","odd":"2.62","precisa":"38%","estimo":"43%","veredito":"Cautela"},
    {"mercado":"Under 2.5 gols","odd":"1.50","precisa":"67%","estimo":"57%","veredito":"-EV"},
  ],
  "verdict":("ATENÇÃO: este é o jogo em que MODELO e MERCADO mais discordam da nossa série. Meu modelo "
    "vê Mirassol favorito e jogo aberto (Mir 55%, Over 2.5 50%); o mercado vê um jogo MUITO mais "
    "truncado e equilibrado (Mir só 46%, Under 2.5 em 64%, BTTS-Não). Escalações confirmadas e "
    "completas dos dois lados. O ponto honesto: essa divergência quase certamente vem de uma FRAQUEZA "
    "do meu modelo aqui — ele ainda carrega a super-temporada 2025 do Mirassol, enquanto na tabela de "
    "2026 o Mirassol vinha lá embaixo (16º). Ou seja, o mercado provavelmente está mais certo, e eu "
    "DEFIRO a ele: jogo tende a ser fechado e de poucos gols. Não trataria o 'valor' que meu modelo "
    "aponta (Mirassol / Over) como valor real — é miragem do modelo super-avaliar o Mirassol."),
  "tips":[
    "Leitura honesta: quando modelo e mercado divergem MUITO (como aqui), o mercado costuma vencer. Este é um caso desses.",
    "A causa provável: o modelo pondera a excelente campanha 2025 do Mirassol, mas em 2026 eles vinham em 16º. Ele super-avalia o mandante.",
    "Por isso marquei Mirassol e Over como 'Cautela', não 'Valor' — o número do modelo está inflado nesse jogo específico.",
    "Se for seguir alguém, siga o mercado: jogo truncado, tendência de Under 2.5 e possível BTTS-Não.",
    "Falta o árbitro pra fechar os cartões. Mas o recado principal do jogo é a divergência — e a humildade de reconhecer o limite do modelo.",
  ],
}
print("OK:", build(ctx))
