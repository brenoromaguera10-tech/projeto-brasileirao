"""
Análise de confronto — Brasileirão Série A 2026
Uso: analisar("Palmeiras", "Corinthians")
     analisar("Vasco", "Flamengo", odds=(3.1,3.2,2.3))          # blend com mercado (opcional)
     analisar("Bahia", "Santos", adj={"home_att":-0.12})         # ajuste por desfalque (log-escala)

Modelo em cache (modelo.pkl). Recriar com: python3 analise.py --refit
"""
import os, sys, pickle
import numpy as np
from brasileirao_model import load, fit, norm_team, score_matrix, markets

CACHE = os.path.join(os.path.dirname(__file__), "modelo.pkl")

def get_model(refit=False):
    if not refit and os.path.exists(CACHE):
        return pickle.load(open(CACHE, "rb"))
    m = fit(load())
    pickle.dump(m, open(CACHE, "wb"))
    return m

def _bar(p, width=20):
    n = int(round(p*width)); return "█"*n + "·"*(width-n)

def analisar(home, away, odds=None, adj=None, model=None, texto=True):
    m = model or get_model()
    known = set(m["teams"])
    h = norm_team(home, known); a = norm_team(away, known)
    idx, att, dfn = m["idx"], m["att"], m["def"]
    # xG base
    lh = att[idx[h]] - dfn[idx[a]] + m["home"]
    la = att[idx[a]] - dfn[idx[h]]
    # ajustes por escalação/desfalque (nudges em log-escala)
    adj = adj or {}
    lh += adj.get("home_att",0) - adj.get("away_def",0)
    la += adj.get("away_att",0) - adj.get("home_def",0)
    lh, la = float(np.exp(lh)), float(np.exp(la))
    M = score_matrix(lh, la, m["rho"]); mk = markets(M)
    base = m.get("btts_base",0.48)
    btts = 0.2*mk["btts"] + 0.8*base
    probs = {"casa":mk["home"],"empate":mk["draw"],"fora":mk["away"]}
    if odds:
        # peso ótimo por backtest 2025-26: ~85% mercado / 15% modelo (o mercado é mais preciso)
        WM = 0.15
        oh,od,oa = odds; inv=np.array([1/oh,1/od,1/oa]); imp=inv/inv.sum()
        probs = {"casa":WM*probs["casa"]+(1-WM)*imp[0],
                 "empate":WM*probs["empate"]+(1-WM)*imp[1],
                 "fora":WM*probs["fora"]+(1-WM)*imp[2]}
    data = {"home":h,"away":a,"xg_home":lh,"xg_away":la,"probs":probs,
            "btts":btts,"btts_nao":1-btts,"over25":mk["over25"],"over15":mk["over15"],
            "under25":1-mk["over25"],"top_scores":mk["top_scores"],
            "favorito":max(probs,key=probs.get)}
    if not texto: return data

    fav = data["favorito"]
    favnome = {"casa":h,"empate":"Empate","fora":a}[fav]
    dom = "clássico equilibrado" if abs(probs["casa"]-probs["fora"])<0.12 else \
          ("mando forte" if fav=="casa" else "visitante mais forte")
    L=[]
    L.append(f"⚽ {h}  x  {a}  —  Brasileirão Série A")
    L.append("─"*46)
    L.append(f"Gols esperados (xG):  {h} {lh:.2f}  ×  {la:.2f} {a}   (total {lh+la:.2f})")
    L.append("")
    L.append("① RESULTADO (1x2)   ▸ confiança ALTA (≈ nível de mercado)")
    L.append(f"   Casa   {probs['casa']*100:4.0f}%  {_bar(probs['casa'])}")
    L.append(f"   Empate {probs['empate']*100:4.0f}%  {_bar(probs['empate'])}")
    L.append(f"   Fora   {probs['fora']*100:4.0f}%  {_bar(probs['fora'])}")
    L.append(f"   → Favorito: {favnome}")
    L.append("")
    L.append("② AMBOS MARCAM   ▸ confiança BAIXA (perto da média histórica)")
    L.append(f"   SIM {btts*100:4.0f}%  {_bar(btts)}")
    L.append(f"   NÃO {(1-btts)*100:4.0f}%  {_bar(1-btts)}")
    L.append("")
    L.append("③ GOLS (apoio)")
    L.append(f"   Over 1.5 {mk['over15']*100:3.0f}%  |  Over 2.5 {mk['over25']*100:3.0f}%  |  Under 2.5 {(1-mk['over25'])*100:3.0f}%")
    ts=" · ".join(f"{i}-{j} {p*100:.0f}%" for (i,j),p in data['top_scores'][:4])
    L.append(f"   Placares prováveis: {ts}")
    L.append("")
    L.append(f"PRÉ-ANÁLISE: {dom}. " + (
        f"{favnome} chega como favorito. " if fav!="empate" else "Jogo muito parelho. ") +
        f"Expectativa de {'muitos' if lh+la>2.7 else ('poucos' if lh+la<2.2 else 'um volume moderado de')} gols "
        f"({lh+la:.1f} no total).")
    L.append("↻ Me mande escalações/desfalques/árbitro que eu recalibro os números.")
    return "\n".join(L)

if __name__ == "__main__":
    if "--refit" in sys.argv:
        m = get_model(refit=True); print("Modelo treinado e salvo. btts_base=%.3f"%m["btts_base"]); sys.exit()
    h = sys.argv[1] if len(sys.argv)>1 else "Palmeiras"
    a = sys.argv[2] if len(sys.argv)>2 else "Corinthians"
    print(analisar(h,a))
