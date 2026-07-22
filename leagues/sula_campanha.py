#!/usr/bin/env python3
"""
Sula 2026 — modelo v3 por campanha continental (FootyStats Team Stats).

Base: sula_stats.json (Sudamericana + Libertadores 2026, com splits casa/fora).
Ratings de ataque/defesa POR SPLIT (mando embutido nas médias casa/fora da
liga — sem multiplicador extra), com encolhimento duplo:
  split -> campanha total (K2) -> média da liga (K)

PARAMS PROVISÓRIOS (declarados, sem backtest próprio da Sula):
  SOS_LIB  crédito de força de tabela p/ campanhas na Libertadores
  K, K2    encolhimento bayesiano (amostras de 3-10 jogos)
  RHO      correção Dixon-Coles (Série A)
Confiança: BAIXA no 1x2; o fechamento com odds domina (blend 90% mercado).
"""
import json, math, os

SOS_LIB, K, K2, RHO = 1.15, 4.0, 3.0, 0.0152

_dir = os.path.dirname(os.path.abspath(__file__))
_S = json.load(open(os.path.join(_dir, "sula_stats.json"), encoding="utf-8"))
LIGA = _S["_liga"]
MU, MU_H, MU_A = LIGA["gols_pg_time"], LIGA["gols_home_pg"], LIGA["gols_away_pg"]

# nome usado nas análises -> nome FootyStats
NAMES = {
    "Independiente Medellin": "Deportivo Independiente Medellín",
    "Vasco da Gama": "CR Vasco da Gama",
    "Lanus": "CA Lanús",
    "Cienciano": "Club Cienciano",
    "Sporting Cristal": "Club Sporting Cristal SAC",
    "RB Bragantino": "Clube Atlético Bragantino",
    "Gremio": "Grêmio FB Porto Alegrense",
    "Santos": "Santos FC Sao Paulo",
    "Tigre": "CA Tigre",
    "Boca Juniors": "CA Boca Juniors",
}

def _team(name):
    t = _S.get(NAMES.get(name, name)) or _S.get(name)
    if not t:
        raise ValueError(f"Time sem stats: '{name}'. Rodar build_sula_from_teamstats.py com os dois CSVs.")
    return t

def _ratings(name, lado):  # lado: 'home' | 'away'
    t = _team(name)
    sos = SOS_LIB if t["source"] == "libertadores" else 1.0
    att_o = (t["gf_pg"] / MU) * sos
    def_o = (t["ga_pg"] / MU) / sos
    n = t["games"]
    att_o = (att_o*n + K) / (n + K)          # encolhe p/ média da liga
    def_o = (def_o*n + K) / (n + K)
    if lado == "home":
        ns = t["games_home"]
        att_s = (t["gf_home_pg"] / MU_H) * sos
        def_s = (t["ga_home_pg"] / MU_A) / sos
    else:
        ns = t["games_away"]
        att_s = (t["gf_away_pg"] / MU_A) * sos
        def_s = (t["ga_away_pg"] / MU_H) / sos
    att = (att_s*ns + att_o*K2) / (ns + K2)  # split encolhe p/ campanha total
    dfs = (def_s*ns + def_o*K2) / (ns + K2)
    return att, dfs

def dc_tau(hg, ag, lh, la, rho):
    if hg == 0 and ag == 0: return 1 - lh*la*rho
    if hg == 0 and ag == 1: return 1 + lh*rho
    if hg == 1 and ag == 0: return 1 + la*rho
    if hg == 1 and ag == 1: return 1 - rho
    return 1.0

def _pois(l, k): return math.exp(-l)*l**k/math.factorial(k)

def analisar_sula(home, away, neutral=False):
    ah, dh = _ratings(home, "home")
    aa, da = _ratings(away, "away")
    mu_h, mu_a = (MU, MU) if neutral else (MU_H, MU_A)   # final única: campo neutro
    lh, la = mu_h*ah*da, mu_a*aa*dh
    N = 9
    grid = [[_pois(lh,i)*_pois(la,j)*dc_tau(i,j,lh,la,RHO) for j in range(N)] for i in range(N)]
    s = sum(map(sum, grid)); grid = [[p/s for p in row] for row in grid]
    pc = sum(grid[i][j] for i in range(N) for j in range(N) if i > j)
    pf = sum(grid[i][j] for i in range(N) for j in range(N) if i < j)
    probs = {"casa": pc, "empate": 1-pc-pf, "fora": pf}
    btts = sum(grid[i][j] for i in range(1,N) for j in range(1,N))
    over15 = sum(grid[i][j] for i in range(N) for j in range(N) if i+j >= 2)
    over25 = sum(grid[i][j] for i in range(N) for j in range(N) if i+j >= 3)
    top = sorted((((i,j), grid[i][j]) for i in range(N) for j in range(N)), key=lambda x: -x[1])[:6]
    return {"home": home, "away": away, "xg_home": lh, "xg_away": la,
            "probs": probs, "btts": btts, "btts_nao": 1-btts,
            "over25": over25, "over15": over15, "under25": 1-over25,
            "top_scores": top, "favorito": max(probs, key=probs.get)}

if __name__ == "__main__":
    for h, a in [("Independiente Medellin","Vasco da Gama"),
                 ("Lanus","Cienciano"),
                 ("Sporting Cristal","RB Bragantino")]:
        d = analisar_sula(h, a); p = d["probs"]
        print(f"{h} x {a}: xG {d['xg_home']:.2f}-{d['xg_away']:.2f} | "
              f"1x2 {p['casa']*100:.0f}/{p['empate']*100:.0f}/{p['fora']*100:.0f} | "
              f"BTTS {d['btts']*100:.0f}% | O2.5 {d['over25']*100:.0f}%")
