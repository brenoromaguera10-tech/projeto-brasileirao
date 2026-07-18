"""
Motor de probabilidades — Brasileirão Série A
Modelo Dixon-Coles (Poisson bivariado com correção de placares baixos),
ratings de ataque/defesa por time, vantagem de mando e peso por recência.

Saídas por confronto: 1x2, Ambos Marcam (BTTS), Over/Under, gols esperados,
placares mais prováveis. Foco: 1x2 e BTTS data-driven.
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import poisson

CSV = "/root/.claude/uploads/47781a5b-618c-5f57-879a-a68aaaa8d809/477819a5-BRA.csv"

# ---- normalização de nomes (usuário pode digitar de forma livre) -------------
ALIASES = {
    "flamengo":"Flamengo RJ","fla":"Flamengo RJ","mengao":"Flamengo RJ",
    "botafogo":"Botafogo RJ","fogao":"Botafogo RJ","botafogo rj":"Botafogo RJ",
    "sao paulo":"Sao Paulo","são paulo":"Sao Paulo","spfc":"Sao Paulo","tricolor paulista":"Sao Paulo",
    "atletico-mg":"Atletico-MG","atlético-mg":"Atletico-MG","atletico mg":"Atletico-MG","galo":"Atletico-MG","cam":"Atletico-MG",
    "athletico-pr":"Athletico-PR","athletico":"Athletico-PR","athletico pr":"Athletico-PR","cap":"Athletico-PR","furacao":"Athletico-PR",
    "bragantino":"Bragantino","red bull bragantino":"Bragantino","rb bragantino":"Bragantino","massa bruta":"Bragantino",
    "vasco":"Vasco","vasco da gama":"Vasco","gigante da colina":"Vasco",
    "gremio":"Gremio","grêmio":"Gremio","imortal":"Gremio",
    "internacional":"Internacional","inter":"Internacional","colorado":"Internacional",
    "chapecoense":"Chapecoense-SC","chapecoense-sc":"Chapecoense-SC","chape":"Chapecoense-SC",
    "vitoria":"Vitoria","vitória":"Vitoria",
    "palmeiras":"Palmeiras","verdao":"Palmeiras","porco":"Palmeiras",
    "corinthians":"Corinthians","timao":"Corinthians","timão":"Corinthians",
    "fluminense":"Fluminense","flu":"Fluminense",
    "cruzeiro":"Cruzeiro","raposa":"Cruzeiro",
    "santos":"Santos","peixe":"Santos",
    "bahia":"Bahia","tricolor de aco":"Bahia",
    "mirassol":"Mirassol",
    "coritiba":"Coritiba","coxa":"Coritiba",
    "remo":"Remo","leao azul":"Remo",
}
def norm_team(name, known):
    if name in known: return name
    k = name.strip().lower()
    if k in ALIASES and ALIASES[k] in known: return ALIASES[k]
    # tentativa por prefixo
    for t in known:
        if t.lower().startswith(k) or k in t.lower():
            return t
    raise ValueError(f"Time não reconhecido: '{name}'. Conhecidos: {sorted(known)}")

# ---- carregamento ------------------------------------------------------------
def load():
    df = pd.read_csv(CSV)
    df = df.dropna(subset=["HG","AG"]).copy()
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y", errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    df["HG"] = df["HG"].astype(int); df["AG"] = df["AG"].astype(int)
    return df

# ---- correção Dixon-Coles para placares baixos -------------------------------
def dc_tau(hg, ag, lh, la, rho):
    if hg==0 and ag==0: return 1 - lh*la*rho
    if hg==0 and ag==1: return 1 + lh*rho
    if hg==1 and ag==0: return 1 + la*rho
    if hg==1 and ag==1: return 1 - rho
    return 1.0

# ---- ajuste do modelo (MLE ponderado por recência) ---------------------------
def fit(df, ref_date=None, xi=0.0018, l2=0.02, season_boost=1.0):
    teams = sorted(set(df["Home"]) | set(df["Away"]))
    idx = {t:i for i,t in enumerate(teams)}
    n = len(teams)
    if ref_date is None: ref_date = df["Date"].max()
    age = (ref_date - df["Date"]).dt.days.values.astype(float)
    w = np.exp(-xi * age)                       # peso por recência
    # boost da temporada corrente: multiplica o peso dos jogos da última temporada
    # presente nos dados (combate o "efeito 2025" de super-avaliar quem caiu de rendimento)
    if season_boost != 1.0 and "Season" in df.columns:
        cur = df["Season"].max()
        w = w * np.where(df["Season"].values == cur, season_boost, 1.0)
    hi = df["Home"].map(idx).values
    ai = df["Away"].map(idx).values
    hg = df["HG"].values; ag = df["AG"].values

    # params: [att(n), def(n), home_adv, rho]
    def unpack(p):
        att = p[:n]; dfn = p[n:2*n]; home = p[2*n]; rho = p[2*n+1]
        att = att - att.mean()                  # identificabilidade
        dfn = dfn - dfn.mean()
        return att, dfn, home, rho

    def nll(p):
        att, dfn, home, rho = unpack(p)
        rho = np.clip(rho, -0.2, 0.2)
        lh = np.exp(att[hi] - dfn[ai] + home)
        la = np.exp(att[ai] - dfn[hi])
        lh = np.clip(lh, 1e-6, 12); la = np.clip(la, 1e-6, 12)
        ll = hg*np.log(lh) - lh + ag*np.log(la) - la          # poisson (sem termo fatorial, constante)
        # correção DC só afeta placares <=1
        tau = np.ones_like(lh)
        m = (hg<=1)&(ag<=1)
        for j in np.where(m)[0]:
            tau[j] = max(dc_tau(hg[j],ag[j],lh[j],la[j],rho), 1e-6)
        ll = ll + np.log(tau)
        pen = l2*(np.sum(att**2)+np.sum(dfn**2))              # shrinkage p/ times com poucos dados
        return -np.sum(w*ll) + pen

    p0 = np.concatenate([np.zeros(n), np.zeros(n), [0.25], [-0.05]])
    res = minimize(nll, p0, method="L-BFGS-B",
                   bounds=[(-3,3)]*(2*n)+[(-1,1),(-0.2,0.2)],
                   options={"maxiter":500})
    att, dfn, home, rho = unpack(res.x)
    # base rate de BTTS ponderado por recência (para calibrar o BTTS, que tem sinal fraco)
    btts_y = ((hg>0)&(ag>0)).astype(float)
    btts_base = float(np.sum(w*btts_y)/np.sum(w))
    return {"teams":teams,"idx":idx,"att":att,"def":dfn,"home":home,"rho":rho,
            "xi":xi,"ref_date":ref_date,"ll":-res.fun,"btts_base":btts_base}

# ---- matriz de placares e mercados -------------------------------------------
def score_matrix(lh, la, rho, kmax=12):
    ph = poisson.pmf(np.arange(kmax+1), lh)
    pa = poisson.pmf(np.arange(kmax+1), la)
    M = np.outer(ph, pa)
    for i in (0,1):
        for j in (0,1):
            M[i,j] *= dc_tau(i,j,lh,la,rho)
    return M / M.sum()

def markets(M):
    kmax = M.shape[0]-1
    home = np.tril(M,-1).sum(); draw = np.trace(M); away = np.triu(M,1).sum()
    btts = 1 - (M[0,:].sum() + M[:,0].sum() - M[0,0])
    tot = np.add.outer(np.arange(kmax+1), np.arange(kmax+1))
    over25 = M[tot>=3].sum(); over15 = M[tot>=2].sum(); over35 = M[tot>=4].sum()
    # placares mais prováveis
    flat = [((i,j), M[i,j]) for i in range(kmax+1) for j in range(kmax+1)]
    flat.sort(key=lambda x:-x[1])
    return {"home":home,"draw":draw,"away":away,"btts":btts,
            "over15":over15,"over25":over25,"over35":over35,
            "top_scores":flat[:6]}

def predict(model, home_team, away_team, blend_odds=None, blend_w=0.5):
    known = set(model["teams"])
    h = norm_team(home_team, known); a = norm_team(away_team, known)
    att, dfn, idx = model["att"], model["def"], model["idx"]
    lh = float(np.exp(att[idx[h]] - dfn[idx[a]] + model["home"]))
    la = float(np.exp(att[idx[a]] - dfn[idx[h]]))
    M = score_matrix(lh, la, model["rho"])
    mk = markets(M)
    out = {"home_team":h,"away_team":a,"xg_home":lh,"xg_away":la,**mk}
    # calibração do BTTS: sinal do modelo é fraco -> 20% modelo + 80% base rate
    base = model.get("btts_base", 0.48)
    out["btts_raw"] = mk["btts"]
    out["btts"] = 0.2*mk["btts"] + 0.8*base
    # blend opcional com odds de mercado (de-vig), se o usuário fornecer
    if blend_odds:
        oh,od,oa = blend_odds
        inv = np.array([1/oh,1/od,1/oa]); imp = inv/inv.sum()
        out["home"] = blend_w*out["home"] + (1-blend_w)*imp[0]
        out["draw"] = blend_w*out["draw"] + (1-blend_w)*imp[1]
        out["away"] = blend_w*out["away"] + (1-blend_w)*imp[2]
        out["market_probs"] = imp.tolist()
    return out

if __name__ == "__main__":
    df = load()
    print("Jogos:", len(df), "| Times:", df['Home'].nunique())
    m = fit(df)
    print("Home advantage (gamma):", round(m["home"],3), "| rho:", round(m["rho"],3))
    # ranking de força: att + def (def alto = defesa boa; maior soma = time mais forte)
    strength = sorted(zip(m["teams"], m["att"]+m["def"]), key=lambda x:-x[1])
    cur = ['Palmeiras','Flamengo RJ','Cruzeiro','Fluminense','Sao Paulo','Bahia',
           'Botafogo RJ','Bragantino','Corinthians','Atletico-MG','Mirassol',
           'Internacional','Gremio','Santos','Vasco','Vitoria','Athletico-PR',
           'Coritiba','Chapecoense-SC','Remo']
    print("\nForça relativa (times 2026, ataque-defesa, maior=melhor):")
    for t,s in strength:
        if t in cur: print(f"  {t:16s} {s:+.3f}")
