#!/usr/bin/env python3
"""
Conversor genérico FootyStats -> formato do motor (BRA.csv).

Uso:
    python3 build_footystats.py <config.json> <match_stats.csv>

Entrada : Match Stats CSV do FootyStats (footystats.org > download-stats-csv,
          página central "Match Stats CSV" da liga/copa).
Saída   : <code>.csv  no formato do motor (Date,Home,Away,HG,AG,Res,Avg odds)
          <code>_stats.json  com médias por time (chutes, escanteios, faltas,
          cartões) para o stats_model.

Config-driven (roadmap_multiliga): um JSON por liga, zero código novo por liga.
"""
import csv, json, re, sys
from collections import defaultdict
from datetime import datetime

# colunas do Match Stats CSV do FootyStats (nomes usuais; conferir no arquivo)
COL = {
    "date": "date_GMT",
    "status": "status",
    "home": "home_team_name",
    "away": "away_team_name",
    "hg": "home_team_goal_count",
    "ag": "away_team_goal_count",
    "h_corners": "home_team_corner_count",
    "a_corners": "away_team_corner_count",
    "h_yellow": "home_team_yellow_cards",
    "a_yellow": "away_team_yellow_cards",
    "h_red": "home_team_red_cards",
    "a_red": "away_team_red_cards",
    "h_shots": "home_team_shots",
    "a_shots": "away_team_shots",
    "h_sot": "home_team_shots_on_target",
    "a_sot": "away_team_shots_on_target",
    "h_fouls": "home_team_fouls",
    "a_fouls": "away_team_fouls",
    "odds_h": "odds_ft_home_team_win",
    "odds_d": "odds_ft_draw",
    "odds_a": "odds_ft_away_team_win",
}

def parse_date(s):
    # FootyStats: "Jul 21 2026 - 7:30pm" (às vezes só "Jul 21 2026")
    s = s.strip()
    for fmt in ("%b %d %Y - %I:%M%p", "%b %d %Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    m = re.match(r"(\w{3} \d{1,2} \d{4})", s)
    if m:
        return datetime.strptime(m.group(1), "%b %d %Y")
    raise ValueError(f"data não reconhecida: '{s}'")

def num(row, key, default=None):
    v = row.get(COL[key], "")
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

def main(cfg_path, csv_path):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    code, season = cfg["code"], str(cfg.get("season", ""))
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
    if not rows:
        sys.exit("CSV vazio.")
    faltando = [v for v in COL.values() if v not in rows[0]]
    if faltando:
        print(f"AVISO: colunas ausentes no CSV (seguindo sem elas): {faltando}")

    out_rows, stats = [], defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r.get(COL["status"], "complete").strip().lower() not in ("complete", "finished"):
            continue  # só jogos encerrados entram na base
        try:
            d = parse_date(r[COL["date"]])
        except Exception as ex:
            print(f"AVISO: linha pulada ({ex})"); continue
        h, a = r[COL["home"]].strip(), r[COL["away"]].strip()
        hg, ag = num(r, "hg"), num(r, "ag")
        if hg is None or ag is None:
            continue
        hg, ag = int(hg), int(ag)
        res = "H" if hg > ag else ("A" if ag > hg else "D")
        out_rows.append({
            "Country": cfg.get("country", "South America"),
            "League": cfg["name"], "Season": season or d.year,
            "Date": d.strftime("%d/%m/%Y"), "Time": d.strftime("%H:%M"),
            "Home": h, "Away": a, "HG": hg, "AG": ag, "Res": res,
            "AvgCH": num(r, "odds_h", ""), "AvgCD": num(r, "odds_d", ""),
            "AvgCA": num(r, "odds_a", ""),
        })
        # médias por time (mando indiferente: for/against)
        for team, opp, pref, opref in ((h, a, "h_", "a_"), (a, h, "a_", "h_")):
            s = stats[team]
            for k, col in (("shots", "shots"), ("sot", "sot"), ("corners", "corners"),
                           ("fouls", "fouls"), ("yellow", "yellow"), ("red", "red")):
                v = num(r, pref + col)
                if v is not None: s[k + "_for"].append(v)
                v2 = num(r, opref + col)
                if v2 is not None and k in ("shots", "sot", "corners"):
                    s[k + "_against"].append(v2)

    out_csv = cfg.get("out_csv", f"{code.upper()}.csv")
    cols = ["Country","League","Season","Date","Time","Home","Away","HG","AG","Res","AvgCH","AvgCD","AvgCA"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out_rows)

    stats_out = {t: {k: round(sum(v)/len(v), 2) for k, v in s.items() if v} |
                    {"games": len(s.get("shots_for", s.get("corners_for", [])))}
                 for t, s in sorted(stats.items())}
    out_stats = cfg.get("out_stats", f"{code}_stats.json")
    json.dump(stats_out, open(out_stats, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print(f"OK: {len(out_rows)} jogos -> {out_csv}; {len(stats_out)} times -> {out_stats}")
    print("Times no CSV:", ", ".join(sorted(stats_out)))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
