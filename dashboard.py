"""
Gerador de Dashboard de análise de jogo — Brasileirão.
Monta um HTML visual (degradê de cor por percentual, selos de confiança,
comparação com o mercado, dicas de leitura) a partir do modelo + contexto do jogo.

Uso: build(ctx) -> caminho do HTML. Ver exemplo no final.
"""
import os, html
import numpy as np
from analise import analisar, get_model

def pct_color(p):
    """0%->vermelho, 50%->verde-limão, 100%->verde. Sem âmbar (reservado ao ouro da marca)."""
    p = max(0.0, min(1.0, p))
    hue = (p/0.5)*96 if p < 0.5 else 96 + ((p-0.5)/0.5)*44   # 0 -> 96 (limão) -> 140
    return f"hsl({hue:.0f} 60% 45%)"

def bar(p, label_left, label_right=None, big=False):
    c = pct_color(p); w = p*100
    h = "22px" if big else "16px"
    right = f'<span class="bR">{label_right}</span>' if label_right else ""
    return (f'<div class="barrow"><span class="bL">{label_left}</span>'
            f'<div class="track" style="height:{h}"><div class="fill" style="width:{w:.1f}%;'
            f'background:{c}"></div><span class="bpct">{p*100:.0f}%</span></div>{right}</div>')

def conf_badge(level):
    m = {"ALTA":("#1f9d55","conf-alta"),"MÉDIA":("#c98a1a","conf-med"),
         "BAIXA":("#c0392b","conf-baixa")}
    col,cls = m[level]
    return f'<span class="badge {cls}">CONFIANÇA {level}</span>'

def form_chips(seq):
    """Entrada em convenção inglesa (W=win, D=draw, L=loss) -> exibe V/E/D em PT.
    Também aceita 'V' (vitória) e 'E' (empate) em PT por conveniência."""
    out=[]
    for r in seq:
        r=r.upper()
        if r in("W","V"):   cls="w"; t="V"   # vitória -> verde
        elif r in("D",):    cls="d"; t="E"   # draw (inglês) -> empate/cinza
        elif r in("E",):    cls="d"; t="E"   # empate (pt)
        elif r in("L",):    cls="l"; t="D"   # loss -> derrota/vermelho
        else:               cls="q"; t="?"
        out.append(f'<span class="chip {cls}">{t}</span>')
    return "".join(out)

def verdict_color(v):
    return {"valor":"#1f9d55","justo":"#c98a1a","sem valor":"#c0392b",
            "na trave":"#c98a1a","-ev":"#c0392b"}.get(v.lower(),"#a99e86")

def build(ctx, outdir="/home/claude"):
    m = get_model()
    d = analisar(ctx["home_key"], ctx["away_key"], odds=ctx.get("odds_1x2"), model=m, texto=False)
    H, A = ctx["home"], ctx["away"]
    xgh, xga = d["xg_home"], d["xg_away"]
    tot = xgh+xga
    pc, pe, pf = d["probs"]["casa"], d["probs"]["empate"], d["probs"]["fora"]
    btts, over25, over15 = d["btts"], d["over25"], d["over15"]
    fav = {"casa":H,"empate":"Empate","fora":A}[d["favorito"]]

    # placares
    scores = " · ".join(f"{i}-{j} <b>{p*100:.0f}%</b>" for (i,j),p in d["top_scores"][:5])

    # tabela de valor
    vrows=""
    for r in ctx.get("value",[]):
        vc = verdict_color(r["veredito"])
        vrows += (f'<tr><td class="vm">{html.escape(r["mercado"])}</td>'
                  f'<td>{r["odd"]}</td><td>{r["precisa"]}</td><td>{r["estimo"]}</td>'
                  f'<td><span class="vpill" style="background:{vc}22;color:{vc};border:1px solid {vc}55">{html.escape(r["veredito"])}</span></td></tr>')

    # cartões
    cards = ctx.get("cards",{})
    card_bars=""
    for lin,(mk,me) in cards.get("linhas",{}).items():
        card_bars += (f'<div class="cardline"><span class="cl">{lin}</span>'
                      f'<div class="ctwo"><div class="cmini"><span>mercado</span>{bar(mk,"")}</div>'
                      f'<div class="cmini"><span>modelo</span>{bar(me,"")}</div></div></div>')

    tips = "".join(f'<li>{html.escape(t)}</li>' for t in ctx.get("tips",[]))

    # ---- bloco de estatísticas: Chutes (nº2) e Escanteios (nº3) --------------
    st = ctx.get("stats")
    stats_block = ""
    if st:
        def sbar(v, vmax, label, val):
            w = max(0.0,min(1.0, v/vmax)); c = pct_color(min(1.0, v/vmax))
            return (f'<div class="barrow"><span class="bL">{label}</span>'
                    f'<div class="track" style="height:18px"><div class="fill" style="width:{w*100:.0f}%;'
                    f'background:{c}"></div><span class="bpct">{val}</span></div></div>')
        corner_bars = "".join(bar(p, f"Over {L}") for L,p in st["over_corners_total"].items())
        stats_block = f"""
      <div class="grid two" style="margin-top:14px">
        <div class="card">
          <h3>⑤ Chutes (por time) {conf_badge('MÉDIA')}</h3>
          <div class="sub">taxas reais 2026 (aiscore) + mando · v1 não modela defesa do adversário</div>
          {sbar(st['shots_home'],20,H[:12],f"{st['shots_home']:.1f}")}
          {sbar(st['shots_away'],20,A[:12],f"{st['shots_away']:.1f}")}
          <div class="scores">Total esperado: <b>{st['shots_total']:.1f}</b> · 1º tempo aprox: {H[:10]} {st['shots_home_1T']:.1f} / {A[:10]} {st['shots_away_1T']:.1f}</div>
        </div>
        <div class="card">
          <h3>⑥ Escanteios (total) {conf_badge('MÉDIA')}</h3>
          <div class="sub">taxas reais 2026 (apwin) · total esperado ~{st['corners_total']:.1f} ({H[:8]} {st['corners_home']:.1f} / {A[:8]} {st['corners_away']:.1f})</div>
          {corner_bars}
        </div>
      </div>"""

    css = """
    *{box-sizing:border-box}
    body{margin:0;background:#080807;color:#e6edf3;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;line-height:1.4}
    .wrap{max-width:820px;margin:0 auto;padding:16px}
    .hero{background:linear-gradient(135deg,#14120d,#1c1810);border:1px solid #332d1c;border-radius:18px;padding:18px 20px;box-shadow:0 10px 40px rgba(0,0,0,.4)}
    .brandbar{display:flex;align-items:center;justify-content:center;gap:9px;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #332d1c}
    .brandbar .bw{font-weight:800;font-size:15px;letter-spacing:3px;color:#e5c15a}
    .brandbar .bw b{color:#d7dce4}
    .hero .teams .vs{background:linear-gradient(180deg,#f9e79f,#e5c15a,#b8860b);-webkit-background-clip:text;background-clip:text;color:transparent!important}
    .hero .comp{color:#a99e86;font-size:12px;letter-spacing:.6px;text-transform:uppercase;text-align:center}
    .hero .teams{display:flex;align-items:center;justify-content:center;gap:16px;margin:8px 0 4px}
    .hero .teams .t{font-size:clamp(19px,5vw,26px);font-weight:800}
    .hero .teams .vs{color:#e5c15a;font-size:14px;font-weight:700}
    .hero .meta{color:#a99e86;font-size:12.5px;text-align:center}
    .hero .xg{display:flex;justify-content:center;gap:10px;margin-top:12px;align-items:center}
    .hero .xg .box{background:#0d0b07;border:1px solid #332d1c;border-radius:10px;padding:7px 14px;font-weight:800;font-size:17px}
    .hero .xg .lab{color:#a99e86;font-size:11px;font-weight:600}
    .grid{display:grid;grid-template-columns:1fr;gap:14px;margin-top:14px}
    @media(min-width:680px){.grid.two{grid-template-columns:1fr 1fr}}
    .card{background:#14120d;border:1px solid #332d1c;border-radius:14px;padding:14px 16px}
    .card h3{margin:0 0 2px;font-size:15px;display:flex;align-items:center;justify-content:space-between;gap:8px}
    .card .sub{color:#a99e86;font-size:11.5px;margin-bottom:10px}
    .badge{font-size:9.5px;font-weight:800;padding:3px 8px;border-radius:999px;letter-spacing:.4px;white-space:nowrap}
    .conf-alta{background:#1f9d5522;color:#39d98a;border:1px solid #1f9d5566}
    .conf-med{background:#c98a1a22;color:#f0b429;border:1px solid #c98a1a66}
    .conf-baixa{background:#c0392b22;color:#ff6b5e;border:1px solid #c0392b66}
    .barrow{display:flex;align-items:center;gap:8px;margin:7px 0}
    .bL{width:66px;font-size:12.5px;color:#d8cfb8;flex:none;text-align:right}
    .bR{font-size:12px;color:#a99e86}
    .track{position:relative;flex:1;background:#0d0b07;border-radius:8px;overflow:hidden;border:1px solid #332d1c}
    .fill{height:100%;border-radius:8px;transition:width .4s}
    .bpct{position:absolute;right:8px;top:50%;transform:translateY(-50%);font-size:11.5px;font-weight:800;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.6)}
    .fav{margin-top:8px;font-size:13px;color:#39d98a;font-weight:700}
    .scores{font-size:13px;color:#d8cfb8;margin-top:4px}
    .forms{display:flex;flex-direction:column;gap:8px}
    .frow{display:flex;align-items:center;gap:8px;font-size:13px}
    .frow .fn{width:92px;font-weight:700}
    .chip{width:22px;height:22px;border-radius:5px;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:800;color:#fff}
    .chip.w{background:#1f9d55}.chip.d{background:#5a6472}.chip.l{background:#c0392b}.chip.q{background:#332d1c;color:#a99e86}
    .rating{margin-left:auto;background:#0d0b07;border:1px solid #332d1c;border-radius:7px;padding:2px 8px;font-weight:800;font-size:12px}
    table{width:100%;border-collapse:collapse;font-size:12.5px}
    th,td{padding:7px 6px;text-align:center;border-bottom:1px solid #332d1c}
    th{color:#a99e86;font-size:10.5px;text-transform:uppercase;letter-spacing:.4px}
    td.vm{text-align:left;font-weight:600}
    .vpill{font-size:10.5px;font-weight:800;padding:2px 8px;border-radius:999px}
    .cardline{margin:8px 0}
    .cardline .cl{font-size:12.5px;font-weight:700;color:#d8cfb8}
    .ctwo{display:flex;gap:12px;margin-top:4px}
    .cmini{flex:1}
    .cmini>span{font-size:10px;color:#a99e86;display:block;margin-bottom:2px}
    .cmini .barrow{margin:0}.cmini .bL{width:0}
    .ref{font-size:12.5px;color:#d8cfb8}
    .ref b{color:#f0b429}
    .verdict{background:linear-gradient(135deg,#12261a,#0d0b07);border:1px solid #1f9d5544;border-radius:14px;padding:14px 16px;margin-top:14px}
    .verdict h3{margin:0 0 6px;font-size:15px;color:#39d98a}
    .verdict p{margin:0;font-size:13.5px;color:#dbe4ee}
    .tips{background:#14120d;border:1px solid #332d1c;border-radius:14px;padding:14px 16px 14px 16px;margin-top:14px}
    .tips h3{margin:0 0 8px;font-size:14px;color:#e5c15a}
    .tips ul{margin:0;padding-left:18px}
    .tips li{font-size:12.8px;color:#d8cfb8;margin:5px 0}
    .legend{display:flex;gap:14px;flex-wrap:wrap;font-size:11px;color:#a99e86;margin-top:12px;justify-content:center}
    .legend .g{display:inline-flex;align-items:center;gap:6px}
    .gradbar{width:80px;height:10px;border-radius:6px;background:linear-gradient(90deg,hsl(0 60% 45%),hsl(96 55% 45%),hsl(140 55% 40%))}
    footer{text-align:center;color:#6f6551;font-size:11px;margin:18px 0 8px}
    """

    body = f"""
    <div class="wrap">
      <div class="hero">
        <div class="brandbar">
          <svg width="30" height="30" viewBox="0 0 200 200"><defs><linearGradient id="agold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f9e79f"/><stop offset=".5" stop-color="#e5c15a"/><stop offset="1" stop-color="#a97b16"/></linearGradient></defs><circle cx="100" cy="96" r="74" stroke="url(#agold)" stroke-width="5" fill="none" opacity=".8"/><path d="M58 168 L100 52 L142 168" stroke="url(#agold)" stroke-width="18" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M78 126 L122 126" stroke="url(#agold)" stroke-width="16" stroke-linecap="round"/><path d="M74 150 L104 96 L128 116 L166 46" stroke="url(#agold)" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M166 46 l-14 3 l7 -11 z" fill="url(#agold)"/></svg>
          <span class="bw"><b>ALPHA</b> TRADER</span>
        </div>
        <div class="comp">{html.escape(ctx.get('comp',''))}</div>
        <div class="teams"><span class="t">{html.escape(H)}</span><span class="vs">VS</span><span class="t">{html.escape(A)}</span></div>
        <div class="meta">{html.escape(ctx.get('meta',''))}</div>
        <div class="xg">
          <div><div class="lab">xG {html.escape(H)}</div><div class="box">{xgh:.2f}</div></div>
          <span style="color:#a99e86">×</span>
          <div><div class="lab">xG {html.escape(A)}</div><div class="box">{xga:.2f}</div></div>
          <div><div class="lab">Total</div><div class="box" style="color:#e5c15a">{tot:.2f}</div></div>
        </div>
      </div>

      <div class="grid two">
        <div class="card">
          <h3>① Resultado (1x2) {conf_badge('ALTA')}</h3>
          <div class="sub">{html.escape(ctx.get('sub_1x2','modelo combinado com o mercado'))}</div>
          {bar(pc, H[:12], big=True)}
          {bar(pe, "Empate", big=True)}
          {bar(pf, A[:12], big=True)}
          <div class="fav">★ Favorito: {html.escape(fav)}</div>
        </div>
        <div class="card">
          <h3>② Ambos Marcam {conf_badge('MÉDIA')}</h3>
          <div class="sub">{html.escape(ctx.get('sub_btts','modelo e mercado convergiram (~51/52%)'))}</div>
          {bar(btts, "Sim", big=True)}
          {bar(1-btts, "Não", big=True)}
          <div style="height:8px"></div>
          <h3 style="font-size:14px">③ Gols</h3>
          {bar(over15, "Over 1.5")}
          {bar(over25, "Over 2.5")}
          {bar(1-over25, "Under 2.5")}
          <div class="scores">Placares: {scores}</div>
        </div>
      </div>

      <div class="grid two">
        <div class="card">
          <h3>Forma recente (últimos 5)</h3>
          <div class="sub">V verde · E cinza · D vermelho</div>
          <div class="forms">
            <div class="frow"><span class="fn">{html.escape(H)}</span>{form_chips(ctx['form_home'])}<span class="rating">{ctx.get('rating_home','')}</span></div>
            <div class="frow"><span class="fn">{html.escape(A)}</span>{form_chips(ctx['form_away'])}<span class="rating">{ctx.get('rating_away','')}</span></div>
          </div>
          <div style="height:10px"></div>
          <div class="ref">🧑‍⚖️ Árbitro: <b>{html.escape(ctx.get('ref','—'))}</b><br>
          Média por jogo: <b>{ctx.get('ref_yellow','—')}</b> amarelos · <b>{ctx.get('ref_red','—')}</b> vermelhos {ctx.get('ref_note','')}</div>
        </div>
        <div class="card">
          <h3>④ Cartões (totais) {conf_badge('BAIXA')}</h3>
          <div class="sub">{html.escape(cards.get('sub','expectativa ~'+str(cards.get('exp','5'))+' · sem histórico por time (leitura de árbitro/contexto)'))}</div>
          {card_bars}
        </div>
      </div>

      {stats_block}

      <div class="card" style="margin-top:14px">
        <h3>Valor vs. odds oferecidas</h3>
        <div class="sub">“Precisa” = probabilidade mínima para a odd pagar (breakeven) · “Estimo” = minha probabilidade</div>
        <table>
          <tr><th>Mercado</th><th>Odd</th><th>Precisa</th><th>Estimo</th><th>Veredito</th></tr>
          {vrows}
        </table>
      </div>

      <div class="verdict">
        <h3>🎯 Veredito</h3>
        <p>{html.escape(ctx.get('verdict',''))}</p>
      </div>

      <div class="tips">
        <h3>💡 Dicas de leitura</h3>
        <ul>{tips}</ul>
      </div>

      <div class="legend">
        <span class="g">Escala de probabilidade: <span class="gradbar"></span> 0% → 100%</span>
      </div>
      <footer><b style="color:#e5c15a;letter-spacing:2px">ALPHA TRADER</b> · probabilidade, não garantia · +18, aposte com responsabilidade<br>motor Dixon-Coles (2012–2026) + odds de mercado · {html.escape(ctx.get('meta',''))}</footer>
    </div>
    """
    doc = f"<!DOCTYPE html><html lang='pt-BR'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{html.escape(H)} x {html.escape(A)} — Dashboard</title><style>{css}</style></head><body>{body}</body></html>"
    path = os.path.join(outdir, f"dashboard-{ctx['slug']}.html")
    open(path,"w").write(doc)
    return path
