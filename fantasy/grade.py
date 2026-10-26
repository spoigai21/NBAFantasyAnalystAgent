#!/usr/bin/env python3
"""Grade every game by every rostered player against that player's OWN expected level.

Why not grade against the league? Because 30 fantasy points is a great night for
Collin Murray-Boyles and a disaster for Giannis. A grade is only useful for buy-low /
sell-high if it answers "did this player beat *himself*", so the baseline here is the
player's own projected points-per-minute times the minutes they actually played.

That split matters. It separates the two reasons a line looks good:
    RATE  — they produced more per minute than they should (skill / efficiency / variance)
    ROLE  — they were simply on the floor longer (minutes, which is the bigger term)
A player riding temporary minutes is a sell-high. A player whose rate collapsed while
minutes held is a buy-low. Collapsing both into one number hides exactly that.

Dispersion is measured from the league's own games, not assumed: fantasy scores are a
sum of counting stats, so variance scales with the mean and resid/sqrt(expected) is
roughly homoscedastic. We take the SD of that statistic empirically and z-score on it.

Usage:
    . ~/.espn-fantasy.env && python3 fantasy/grade.py [--rebuild]
"""
import json, os, sqlite3, statistics, subprocess, sys
from datetime import date, timedelta

LEAGUE, SEASON = "1858125890", "2027"
BASE = (f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/fba/seasons/{SEASON}"
        f"/segments/0/leagues/{LEAGUE}")
DB = os.path.join(os.path.dirname(__file__), "league.db")
# Scoring period 1 was opening night.
SEASON_START = date(2026, 10, 20)
MIN_STAT, GP_STAT = "40", "42"

# Grade bands in standard deviations of the player's own expectation.
BANDS = [(1.5, "ELITE"), (0.5, "GOOD"), (-0.5, "NORMAL"), (-1.5, "POOR"), (-9e9, "AWFUL")]
# Minutes bands as a ratio of projected mpg.
MIN_BANDS = [(1.20, "ROLE-UP"), (1.05, "MINS+"), (0.85, "MINS-OK"),
             (0.60, "MINS-DOWN"), (-1.0, "BENCHED")]


def fetch(url):
    s2, swid = os.environ.get("ESPN_S2"), os.environ.get("ESPN_SWID")
    if not s2 or not swid:
        sys.exit("ESPN_S2 and ESPN_SWID are not set. Source ~/.espn-fantasy.env first.")
    out = subprocess.run(
        ["curl", "-s", "-w", "\\n%{http_code}", url,
         "-H", f"cookie: espn_s2={s2}; SWID={swid}",
         "-H", "accept: application/json", "--max-time", "30"],
        capture_output=True, text=True).stdout
    body, _, code = out.rpartition("\n")
    code = code.strip()
    if code != "200":
        sys.exit("401 — cookies rejected; they expire, ask for fresh ones."
                 if code == "401" else f"HTTP {code} for {url}")
    return json.loads(body)


def band(value, bands):
    for threshold, label in bands:
        if value >= threshold:
            return label
    return bands[-1][1]


def collect():
    """One request per scoring period; returns per-game lines for every rostered player."""
    status = fetch(BASE + "?view=mSettings").get("status", {})
    latest = status.get("latestScoringPeriod") or 1
    rows, teams = [], {}
    for sp in range(1, latest + 1):
        d = fetch(BASE + f"?view=mRoster&view=mTeam&scoringPeriodId={sp}")
        for t in d.get("teams", []):
            teams[t["id"]] = t.get("name") or t.get("abbrev")
        game_day = (SEASON_START + timedelta(days=sp - 1)).isoformat()
        for t in d.get("teams", []):
            for e in t.get("roster", {}).get("entries", []):
                p = e.get("playerPoolEntry", {}).get("player", {})
                for st in p.get("stats", []):
                    # statSplitTypeId 5 = a single game; only present for the period asked.
                    if st.get("statSplitTypeId") != 5 or st.get("scoringPeriodId") != sp:
                        continue
                    stats = st.get("stats") or {}
                    if not stats.get(GP_STAT):
                        continue  # did not play
                    rows.append({
                        "player": p.get("fullName"), "team_id": t["id"],
                        "fantasy_team": teams.get(t["id"]), "period": sp, "date": game_day,
                        "game_id": str(st.get("id") or "")[3:],
                        "min": float(stats.get(MIN_STAT) or 0),
                        "fpts": float(st.get("appliedTotal") or 0),
                    })
        print(f"  period {sp} ({game_day}): {len(rows)} lines so far", file=sys.stderr)
    return rows, latest


def main():
    rows, latest = collect()
    con = sqlite3.connect(DB)
    proj = {n: (pf, pm) for n, pf, pm in con.execute(
        "SELECT name, proj_full, proj_mpg FROM players WHERE proj_mpg > 0")}

    # Expectation and raw residual. Skip today's period: games may still be running.
    graded = []
    for r in rows:
        pf, pm = proj.get(r["player"], (None, None))
        if not pf or not pm or r["min"] < 1:
            r["expected"] = r["z"] = None
            continue
        r["fpm_proj"] = pf / pm
        r["expected"] = r["fpm_proj"] * r["min"]
        r["resid"] = r["fpts"] - r["expected"]
        r["scaled"] = r["resid"] / (r["expected"] ** 0.5) if r["expected"] > 0 else 0.0
        if r["period"] < latest:
            graded.append(r)

    sd = statistics.pstdev([g["scaled"] for g in graded]) or 1.0
    print(f"\nmeasured dispersion: SD(resid/sqrt(expected)) = {sd:.3f} "
          f"over {len(graded)} completed games", file=sys.stderr)

    for r in rows:
        if r.get("expected") is None:
            r["z"], r["grade"], r["min_grade"] = None, "DNP", "DNP"
            continue
        r["z"] = r["scaled"] / sd
        r["grade"] = band(r["z"], BANDS)
        pm = proj[r["player"]][1]
        r["min_ratio"] = r["min"] / pm
        r["min_grade"] = band(r["min_ratio"], MIN_BANDS)
        if r["period"] == latest:
            r["grade"] = "PARTIAL"  # today's slate may be mid-flight

    con.executescript("""
        DROP TABLE IF EXISTS game_grades;
        CREATE TABLE game_grades(
          player TEXT, fantasy_team TEXT, period INT, date TEXT, game_id TEXT,
          min REAL, fpts REAL, expected REAL, resid REAL, z REAL,
          grade TEXT, min_ratio REAL, min_grade TEXT);
        CREATE INDEX idx_gg_player ON game_grades(player);
        CREATE INDEX idx_gg_date ON game_grades(date);
    """)
    con.executemany(
        "INSERT INTO game_grades VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [(r["player"], r["fantasy_team"], r["period"], r["date"], r["game_id"],
          round(r["min"], 1), round(r["fpts"], 1),
          None if r.get("expected") is None else round(r["expected"], 1),
          None if r.get("expected") is None else round(r["resid"], 1),
          None if r.get("z") is None else round(r["z"], 2), r["grade"],
          None if r.get("min_ratio") is None else round(r["min_ratio"], 3),
          r["min_grade"]) for r in rows])

    # Per-player form, from completed games only, with the rate/role split kept separate.
    con.executescript("""
        DROP TABLE IF EXISTS player_form;
        CREATE TABLE player_form(
          player TEXT PRIMARY KEY, fantasy_team TEXT, games INT, fpts_pg REAL,
          expected_pg REAL, form_z REAL, min_ratio REAL, best TEXT, worst TEXT,
          grades TEXT, signal TEXT, note TEXT);
    """)
    by_player = {}
    for g in graded:
        by_player.setdefault(g["player"], []).append(g)

    form = []
    for name, gs in by_player.items():
        gs.sort(key=lambda x: x["period"])
        zs = [g["z"] for g in gs]
        fz = sum(zs) / len(zs)
        mr = sum(g["min_ratio"] for g in gs) / len(gs)
        # Signal: rate and role are different trades. Rate regresses; role may not.
        if fz >= 0.6 and mr >= 1.10:
            sig, note = "SELL HIGH", "beating own rate AND on inflated minutes — both regress"
        elif fz >= 0.6:
            sig, note = "SELL HIGH (rate)", "rate above own level; minutes normal"
        elif mr >= 1.15 and fz > -0.3:
            sig, note = "SELL HIGH (minutes)", "production is borrowed minutes, not rate"
        elif fz <= -0.6 and mr >= 0.90:
            sig, note = "BUY LOW", "rate down but role intact — the fixable kind"
        elif fz <= -0.6:
            sig, note = "AVOID", "rate down AND minutes down — role problem, not variance"
        else:
            sig, note = "HOLD", "within noise of own expectation"
        form.append((name, gs[0]["fantasy_team"], len(gs),
                     round(sum(g["fpts"] for g in gs) / len(gs), 1),
                     round(sum(g["expected"] for g in gs) / len(gs), 1),
                     round(fz, 2), round(mr, 3),
                     max(gs, key=lambda x: x["z"])["grade"],
                     min(gs, key=lambda x: x["z"])["grade"],
                     " ".join(g["grade"][0] + ("+" if g["z"] >= 1.5 else "") for g in gs),
                     sig, note))
    con.executemany("INSERT INTO player_form VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", form)
    con.commit()

    print(f"\ngame_grades: {len(rows)} lines   player_form: {len(form)} players")
    print(f"grade distribution (completed games only):")
    dist = {}
    for g in graded:
        dist[g["grade"]] = dist.get(g["grade"], 0) + 1
    for label in ("ELITE", "GOOD", "NORMAL", "POOR", "AWFUL"):
        n = dist.get(label, 0)
        print(f"  {label:<8}{n:>4}  {n / max(len(graded), 1) * 100:>5.1f}%")


if __name__ == "__main__":
    main()
