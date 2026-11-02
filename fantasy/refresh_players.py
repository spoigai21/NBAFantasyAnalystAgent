#!/usr/bin/env python3
"""Refresh the `players` table in place for every rostered player in the league.

Why this exists: build_db.py rebuilt `players` from a hand-made JSON blob that lived in
a session scratchpad and had NO producer in the repo. Once that scratchpad went away the
documented rebuild (`python3 fantasy/build_db.py`) could never succeed again -- and
because it DROPs tables before reading its input, running it emptied players, research,
game_log, transactions and lloyd_quotes and then crashed. Hit on 31 Oct 2026.

This script is the producer. It is self-contained (ESPN API only), it UPSERTs instead of
dropping, and it writes fantasy/dossier_rows.json so build_db.py has its input back.

Valuation follows CLAUDE.md rule 8. ESPN's projected `appliedAverage` is base scoring
plus GP only -- no OREB, DD, TD, QD or TW, which are this league's extra bonuses. The
fix is to measure the bonus rate from the player's LAST-SEASON actual line and add it:

    proj_full = projected appliedAverage  +  (last-season bonus applied / last-season GP)

Rule 17 says to read `appliedStats` rather than hand-computing, because it is ESPN's own
per-category arithmetic. So the bonus is just the sum of the bonus categories. Verified
on Giannis 31 Oct 2026: OREB 98 + DD 57 + TW 17 = 172 over 36 GP = 4.78/g, against a
stored measured_bonus of 4.75 derived the old hand-computed way.

Usage:  . ~/.espn-fantasy.env && python3 fantasy/refresh_players.py [--dry-run]
"""
import json, os, sqlite3, subprocess, sys

LEAGUE, SEASON = "1858125890", "2027"
LAST = str(int(SEASON) - 1)
BASE = (f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/fba/seasons/{SEASON}"
        f"/segments/0/leagues/{LEAGUE}")
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "league.db")
ROWS_OUT = os.path.join(HERE, "dossier_rows.json")

# appliedStats category ids, read off ESPN's own per-unit weights on 31 Oct 2026.
# Bonus = the categories this league adds on top of ESPN default points scoring.
# GP (42) is EXCLUDED because ESPN's projection already carries it (rule 8).
BONUS_IDS = {"4": "OREB", "37": "DD", "38": "TD", "39": "QD",
             "43": "TW", "7": "EJ", "8": "FF"}
MIN_ID, GP_ID = "40", "42"

# CLAUDE.md rule 28. ESPN's projections run high in this league; a single league-wide
# multiplier fitted on scoring periods 1-9 and tested on 10-11 cut MAE by 2.7% out of
# sample. Per-player corrections were WORSE at every setting tested -- do not add one.
# Refit monthly: if K_PROJ drifts above ~0.95 the correction has served its purpose.
K_PROJ = 0.905

PRO = {1:"ATL",2:"BOS",3:"NOP",4:"CHI",5:"CLE",6:"DAL",7:"DEN",8:"DET",9:"GSW",10:"HOU",
       11:"IND",12:"LAC",13:"LAL",14:"MIA",15:"MIL",16:"MIN",17:"BKN",18:"NYK",19:"ORL",
       20:"PHI",21:"PHX",22:"POR",23:"SAC",24:"SAS",25:"OKC",26:"UTA",27:"WAS",28:"TOR",
       29:"MEM",30:"CHA"}


def fetch(url):
    s2, swid = os.environ.get("ESPN_S2"), os.environ.get("ESPN_SWID")
    if not (s2 and swid):
        sys.exit("ESPN_S2 and ESPN_SWID are not set. . ~/.espn-fantasy.env first.")
    r = subprocess.run(["curl", "-s", "-H", f"cookie: espn_s2={s2}; SWID={swid}", url],
                       capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        sys.exit(f"Bad response (cookies expired? a 401 means ask the user to refresh):\n"
                 f"{r.stdout[:300]}")


def pick(stats, src, split, season):
    for st in stats:
        if (st.get("statSourceId") == src and st.get("statSplitTypeId") == split
                and str(st.get("seasonId")) == season):
            return st
    return None


def main():
    dry = "--dry-run" in sys.argv
    d = fetch(BASE + "?view=mRoster&view=mTeam")
    teams = {t["id"]: (t.get("name") or t.get("abbrev")) for t in d.get("teams", [])}

    out, skipped = [], []
    for t in d.get("teams", []):
        for e in t.get("roster", {}).get("entries", []):
            p = e.get("playerPoolEntry", {}).get("player", {})
            name = p.get("fullName")
            if not name:
                continue
            stats = p.get("stats", [])

            cur = pick(stats, 0, 0, SEASON)          # this season, actual, all games
            prj = pick(stats, 1, 0, SEASON)          # this season, ESPN projection
            lst = pick(stats, 0, 0, LAST)            # last season, actual

            gp = total = per_game = mpg = ppm = None
            if cur:
                cs = cur.get("stats") or {}
                gp = int(cs.get(GP_ID) or 0)
                total = float(cur.get("appliedTotal") or 0)
                mn = float(cs.get(MIN_ID) or 0)
                if gp:
                    per_game = total / gp
                    mpg = mn / gp
                if mn:
                    ppm = total / mn

            proj_base = proj_mpg = None
            if prj:
                proj_base = prj.get("appliedAverage")
                ps = prj.get("stats") or {}
                pgp, pmn = float(ps.get(GP_ID) or 0), float(ps.get(MIN_ID) or 0)
                if pgp:
                    proj_mpg = pmn / pgp

            bonus, bonus_gp = 0.0, 0
            if lst:
                la = lst.get("appliedStats") or {}
                ls = lst.get("stats") or {}
                bonus_gp = int(ls.get(GP_ID) or 0)
                if bonus_gp:
                    bonus = sum(float(la.get(k) or 0) for k in BONUS_IDS) / bonus_gp

            proj_full = (proj_base + bonus) if proj_base is not None else None
            delta = (per_game - proj_full) if (proj_full and per_game is not None) else None
            proj_adj = (proj_full * K_PROJ) if proj_full is not None else None
            delta_adj = ((per_game - proj_adj)
                         if (proj_adj and per_game is not None) else None)

            if proj_base is None:
                skipped.append(name)

            out.append({
                "name": name, "team": teams.get(t["id"]),
                "pro": PRO.get(p.get("proTeamId"), str(p.get("proTeamId"))),
                "inj": p.get("injuryStatus") or "ACTIVE",
                "gp": gp or 0, "total": total, "avg": per_game, "mpg": mpg, "ppm": ppm,
                "base": proj_base, "bonus": bonus, "full": proj_full,
                "projmpg": proj_mpg, "hgp": bonus_gp, "delta": delta,
                "padj": proj_adj, "dadj": delta_adj,
            })

    print(f"{len(out)} rostered players across {len(teams)} fantasy teams")
    if skipped:
        print(f"  no ESPN projection for {len(skipped)}: {', '.join(sorted(skipped)[:8])}"
              f"{' …' if len(skipped) > 8 else ''}")

    if dry:
        print("--dry-run: nothing written")
        return

    con = sqlite3.connect(DB)
    before = {n: (g, pg) for n, g, pg in
              con.execute("SELECT name, gp, per_game FROM players")}
    # UPSERT. Never DROP: research, game_grades and player_form key off these names.
    for r in out:
        con.execute("""INSERT INTO players
            (name, fantasy_team, nba_team, status, gp, total, per_game, mpg, pts_per_min,
             proj_base, measured_bonus, proj_full, proj_mpg, bonus_sample_gp, delta,
             proj_adj, delta_adj)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(name) DO UPDATE SET
              fantasy_team=excluded.fantasy_team, nba_team=excluded.nba_team,
              status=excluded.status, gp=excluded.gp, total=excluded.total,
              per_game=excluded.per_game, mpg=excluded.mpg,
              pts_per_min=excluded.pts_per_min, proj_base=excluded.proj_base,
              measured_bonus=excluded.measured_bonus, proj_full=excluded.proj_full,
              proj_mpg=excluded.proj_mpg, bonus_sample_gp=excluded.bonus_sample_gp,
              delta=excluded.delta, proj_adj=excluded.proj_adj,
              delta_adj=excluded.delta_adj""", (
            r["name"], r["team"], r["pro"], r["inj"], r["gp"],
            None if r["total"] is None else round(r["total"], 1),
            None if r["avg"] is None else round(r["avg"], 2),
            None if r["mpg"] is None else round(r["mpg"], 1),
            None if r["ppm"] is None else round(r["ppm"], 3),
            None if r["base"] is None else round(r["base"], 2), round(r["bonus"], 2),
            None if r["full"] is None else round(r["full"], 1),
            None if r["projmpg"] is None else round(r["projmpg"], 1),
            r["hgp"], None if r["delta"] is None else round(r["delta"], 1),
            None if r["padj"] is None else round(r["padj"], 1),
            None if r["dadj"] is None else round(r["dadj"], 1)))
    con.commit()

    new = [r["name"] for r in out if r["name"] not in before]
    gone = [n for n in before if n not in {r["name"] for r in out}]
    print(f"players table: {con.execute('SELECT COUNT(*) FROM players').fetchone()[0]} rows"
          f"  ({len(new)} new, {len(gone)} no longer rostered but kept)")
    if new:
        print("  new: " + ", ".join(new))
    if gone:
        print("  stale: " + ", ".join(gone))
    con.close()

    json.dump(out, open(ROWS_OUT, "w"), indent=1)
    print(f"wrote {ROWS_OUT} (build_db.py's missing input)")


if __name__ == "__main__":
    main()
