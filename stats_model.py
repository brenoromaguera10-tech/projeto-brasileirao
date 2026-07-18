"""
Modelo de estatísticas por time — Chutes (nº2), Escanteios e Cartões (nº3).
Dados 2026 (médias/jogo): chutes a favor (aiscore), escanteios a favor E contra
(soccerstats), faltas (aiscore). Cartões = faltas do time (propensão) × nível do árbitro.
Estimativa por Poisson. Escanteios já modelam ataque×defesa (for+against).
Limite honesto: chutes ainda só usam taxa "a favor" (falta shots-against);
cartões não capturam efeito de goleada/jogo tranquilo (usa fouls+árbitro).
"""
import numpy as np
from scipy.stats import poisson
from brasileirao_model import norm_team

SHOTS_FOR = {
 "Vasco":17.8,"Bragantino":16.4,"Internacional":15.2,"Flamengo RJ":14.8,"Fluminense":14.7,
 "Cruzeiro":14.2,"Mirassol":14.0,"Bahia":13.9,"Atletico-MG":13.5,"Palmeiras":13.2,
 "Chapecoense-SC":12.8,"Botafogo RJ":12.4,"Athletico-PR":12.2,"Remo":12.2,"Santos":11.8,
 "Sao Paulo":11.8,"Corinthians":11.8,"Gremio":11.3,"Vitoria":11.0,"Coritiba":10.2,
}
CORNERS_FOR = {
 "Athletico-PR":5.17,"Atletico-MG":4.89,"Bahia":5.82,"Botafogo RJ":3.78,"Bragantino":5.56,
 "Chapecoense-SC":3.59,"Corinthians":4.72,"Coritiba":3.22,"Cruzeiro":5.33,"Flamengo RJ":4.53,
 "Fluminense":5.50,"Gremio":3.89,"Internacional":7.11,"Mirassol":5.71,"Palmeiras":6.00,
 "Remo":4.44,"Santos":5.05,"Sao Paulo":6.61,"Vasco":5.16,"Vitoria":3.89,
}
CORNERS_AGAINST = {
 "Athletico-PR":4.50,"Atletico-MG":5.00,"Bahia":5.47,"Botafogo RJ":5.28,"Bragantino":5.17,
 "Chapecoense-SC":6.35,"Corinthians":4.72,"Coritiba":6.50,"Cruzeiro":4.00,"Flamengo RJ":4.88,
 "Fluminense":4.06,"Gremio":4.67,"Internacional":3.94,"Mirassol":4.76,"Palmeiras":5.94,
 "Remo":6.61,"Santos":5.05,"Sao Paulo":4.56,"Vasco":3.84,"Vitoria":4.83,
}
FOULS = {
 "Internacional":16.1,"Bragantino":15.7,"Sao Paulo":14.9,"Bahia":14.6,"Cruzeiro":14.4,
 "Corinthians":14.3,"Palmeiras":14.2,"Athletico-PR":14.1,"Botafogo RJ":14.0,"Fluminense":13.8,
 "Gremio":13.7,"Vitoria":13.6,"Santos":12.8,"Chapecoense-SC":12.7,"Flamengo RJ":12.6,
 "Mirassol":12.6,"Vasco":12.2,"Atletico-MG":11.8,"Remo":11.7,"Coritiba":10.9,
}
LEAGUE_FOULS = np.mean(list(FOULS.values()))     # ~13.5
HOME_F, AWAY_F = 1.08, 0.92

def _k(name): return norm_team(name, set(SHOTS_FOR))
def poisson_over(lam, lines):
    return {L: float(1-poisson.cdf(int(np.floor(L)), lam)) for L in lines}

def shots_team(team, home=True):
    return float(SHOTS_FOR[_k(team)] * (HOME_F if home else AWAY_F))

def corners_match(home, away):
    h,a=_k(home),_k(away)
    # ataque×defesa: média entre o que o time bate e o que o adversário concede
    ch = 0.5*(CORNERS_FOR[h]+CORNERS_AGAINST[a]) * HOME_F
    ca = 0.5*(CORNERS_FOR[a]+CORNERS_AGAINST[h]) * AWAY_F
    return {"home":float(ch),"away":float(ca),"total":float(ch+ca)}

def cards_match(home, away, ref_yellow=4.8, ref_red=0.2, fav_gap=0.0):
    """Cartões totais = nível do árbitro × propensão a faltas × competitividade.
    fav_gap = |P(casa)-P(fora)| do 1x2: jogo desequilibrado (goleada) tende a ser
    mais tranquilo → menos cartões (amortecedor calibrado nos jogos observados)."""
    fi_h = FOULS[_k(home)]/LEAGUE_FOULS
    fi_a = FOULS[_k(away)]/LEAGUE_FOULS
    lvl = ref_yellow + ref_red
    tight = 1 - 0.20*min(1.0, abs(fav_gap))     # 0.20: desequilíbrio reduz cartões
    tot = lvl * (fi_h+fi_a)/2 * tight
    return {"home":float(tot*fi_h/(fi_h+fi_a)),"away":float(tot*fi_a/(fi_h+fi_a)),
            "total":float(tot),"foul_idx_home":float(fi_h),"foul_idx_away":float(fi_a)}

def estimate(home, away, ref_yellow=None, ref_red=None, fav_gap=0.0, half_frac=0.45,
             shot_lines=None, corner_lines=None, card_lines=None):
    sh_h=shots_team(home,True); sh_a=shots_team(away,False)
    cor=corners_match(home,away)
    shot_lines=shot_lines or [7.5,9.5,11.5,13.5]
    corner_lines=corner_lines or [7.5,8.5,9.5,10.5,11.5]
    card_lines=card_lines or [3.5,4.5,5.5,6.5]
    out={"shots_home":sh_h,"shots_away":sh_a,"shots_total":sh_h+sh_a,
         "shots_home_1T":sh_h*half_frac,"shots_away_1T":sh_a*half_frac,
         "corners_home":cor["home"],"corners_away":cor["away"],"corners_total":cor["total"],
         "over_shots_home":poisson_over(sh_h,shot_lines),
         "over_shots_away":poisson_over(sh_a,shot_lines),
         "over_corners_total":poisson_over(cor["total"],corner_lines)}
    if ref_yellow is not None:
        cds=cards_match(home,away,ref_yellow,ref_red or 0.2,fav_gap=fav_gap)
        out.update({"cards_home":cds["home"],"cards_away":cds["away"],"cards_total":cds["total"],
                    "over_cards_total":poisson_over(cds["total"],card_lines)})
    return out

if __name__=="__main__":
    # validação de cartões contra os mercados reais que já vimos
    print("Bahia x Chapecoense (árbitro Zanovelli 5.54/0.42):")
    e=estimate("Bahia","Chapecoense",ref_yellow=5.54,ref_red=0.42)
    print(f"  Cartões total modelo: {e['cards_total']:.1f} (mercado via odds era ~5.0)")
    print(f"  Escanteios total: {e['corners_total']:.1f}")
    print("\nFluminense x Bragantino (árbitro Lacerda 5.18/0.18):")
    e=estimate("Fluminense","Bragantino",ref_yellow=5.18,ref_red=0.18)
    print(f"  Cartões total modelo: {e['cards_total']:.1f} (mercado era ~5.5)")
    over=e['over_cards_total']; print("  Over cartões: "+" | ".join(f"{L} {p*100:.0f}%" for L,p in over.items()))
    print(f"  Escanteios total: {e['corners_total']:.1f}")
