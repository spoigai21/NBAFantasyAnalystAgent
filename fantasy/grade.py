#!/usr/bin/env python3
"""Grade every game by every rostered player against that player's OWN expected level.

Why not grade against the league? Because 30 fantasy points is a great night for
Collin Murray-Boyles and a disaster for Giannis. A grade is only useful for buy-low /
sell-high if it answers "did this player beat *himself*", so the baseline here is the
player's own projected points-per-minute times the minutes they actually played.

That split matters. It separates the three reasons a line looks good:
    RATE  — they produced more per minute than they should (skill / efficiency / variance)
    ROLE  — they were simply on the floor longer (minutes, which is the bigger term)
    USAGE — the offence ran through them more (touches, which is what the coach controls)
A player riding temporary minutes is a sell-high. A player whose rate collapsed while
minutes held is a buy-low. Collapsing them into one number hides exactly that.

Usage is the axis that tells the two apart when minutes look fine. ESPN publishes no
usage rate, but it carries the inputs on both the actual and the projected stat line, so
we build shot equivalents — FGA + 0.44*FTA + TOV, the standard possession-ending count —
per minute, and compare to the player's own projected rate. The distinction it buys:
a player missing shots he is still being given regresses; a player who has quietly
stopped being given them does not. Both look identical on rate and minutes alone.

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
FGA_STAT, FTA_STAT, TOV_STAT = "14", "16", "11"

# Grade bands in standard deviations of the player's own expectation.
BANDS = [(1.5, "ELITE"), (0.5, "GOOD"), (-0.5, "NORMAL"), (-1.5, "POOR"), (-9e9, "AWFUL")]
# Minutes bands as a ratio of projected mpg.
MIN_BANDS = [(1.20, "ROLE-UP"), (1.05, "MINS+"), (0.85, "MINS-OK"),
             (0.60, "MINS-DOWN"), (-1.0, "BENCHED")]
# Usage bands as a ratio of projected shot equivalents per minute.
USG_BANDS = [(1.20, "FED"), (1.05, "USG+"), (0.85, "USG-OK"),
             (0.70, "USG-DOWN"), (-1.0, "FROZEN")]


def shot_equivalents(stats):
    """FGA + 0.44*FTA + TOV — the possessions a player ended. ESPN gives no usage rate."""
    return (float(stats.get(FGA_STAT) or 0)
            + 0.44 * float(stats.get(FTA_STAT) or 0)
            + float(stats.get(TOV_STAT) or 0))


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


def fetch_public(url):
    """Public scoreboard/summary endpoints — no cookies, and failures are not fatal."""
    out = subprocess.run(["curl", "-s", url, "--max-time", "25"],
                         capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except ValueError:
        return {}


def team_context(game_ids):
    """Team possessions per game, so usage can be a real USG%% rather than a proxy.

    The fantasy API gives player stats only. Usage is a *share* of what the team did,
    so the denominator has to come from the public box score: one call per game, keyed
    back to players by name because that spares us a player->NBA-team mapping.
    Verified against a published USG%% column on 26 Oct 2026 — nine of eleven Wizards
    landed within 0.7 of the printed figure, the two misses being sub-4-minute stints
    where the displayed seconds dominate.
    """
    ctx = {}
    for n, gid in enumerate(sorted(game_ids), 1):
        if not gid:
            continue
        j = fetch_public("https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
                         f"/summary?event={gid}")
        box = j.get("boxscore") or {}
        # Overtime adds 5 minutes a period; team minutes scale the usage formula.
        period = (((j.get("header") or {}).get("competitions") or [{}])[0]
                  .get("status") or {}).get("period") or 4
        team_min = (48 + max(0, period - 4) * 5) * 5
        totals = {}
        for t in box.get("teams", []):
            stats = {s.get("name"): s.get("displayValue") for s in t.get("statistics", [])}
            try:
                fga = float(stats["fieldGoalsMade-fieldGoalsAttempted"].split("-")[1])
                fta = float(stats["freeThrowsMade-freeThrowsAttempted"].split("-")[1])
                tov = float(stats.get("totalTurnovers") or stats.get("turnovers") or 0)
            except (KeyError, ValueError, IndexError):
                continue
            totals[t["team"]["abbreviation"]] = fga + 0.44 * fta + tov
        for t in box.get("players", []):
            se = totals.get(t["team"]["abbreviation"])
            if not se:
                continue
            for grp in t.get("statistics", []):
                for a in grp.get("athletes", []):
                    ctx[(gid, a["athlete"]["displayName"])] = (team_min, se)
        if n % 10 == 0:
            print(f"  team context: {n}/{len(game_ids)} games", file=sys.stderr)
    return ctx


def band(value, bands):
    for threshold, label in bands:
        if value >= threshold:
            return label
    return bands[-1][1]


def collect():
    """One request per scoring period; returns per-game lines for every rostered player."""
    status = fetch(BASE + "?view=mSettings").get("status", {})
    latest = status.get("latestScoringPeriod") or 1
    rows, teams, usg_proj, injury = [], {}, {}, {}
    for sp in range(1, latest + 1):
        d = fetch(BASE + f"?view=mRoster&view=mTeam&scoringPeriodId={sp}")
        for t in d.get("teams", []):
            teams[t["id"]] = t.get("name") or t.get("abbrev")
        game_day = (SEASON_START + timedelta(days=sp - 1)).isoformat()
        for t in d.get("teams", []):
            for e in t.get("roster", {}).get("entries", []):
                p = e.get("playerPoolEntry", {}).get("player", {})
                name = p.get("fullName")
                # Later periods overwrite earlier ones, so this ends up current.
                injury[name] = p.get("injuryStatus") or "ACTIVE"
                for st in p.get("stats", []):
                    # statSourceId 1 on the full-season split is ESPN's projection. It
                    # carries FGA/FTA/TOV, so a projected usage rate is recoverable.
                    if (name not in usg_proj and st.get("statSourceId") == 1
                            and st.get("statSplitTypeId") == 0
                            and str(st.get("seasonId")) == SEASON):
                        pstats = st.get("stats") or {}
                        pmin = float(pstats.get(MIN_STAT) or 0)
                        if pmin > 0:
                            usg_proj[name] = shot_equivalents(pstats) / pmin
                    # statSplitTypeId 5 = a single game; only present for the period asked.
                    if st.get("statSplitTypeId") != 5 or st.get("scoringPeriodId") != sp:
                        continue
                    stats = st.get("stats") or {}
                    if not stats.get(GP_STAT):
                        continue  # did not play
                    rows.append({
                        "player": name, "team_id": t["id"],
                        "fantasy_team": teams.get(t["id"]), "period": sp, "date": game_day,
                        # id is "<sourceId><splitTypeId>" + the 9-digit ESPN event id.
                        # Slicing a fixed prefix ate the leading digit; take the tail.
                        "game_id": str(st.get("id") or "")[-9:],
                        "min": float(stats.get(MIN_STAT) or 0),
                        "fpts": float(st.get("appliedTotal") or 0),
                        "shot_eq": shot_equivalents(stats),
                    })
        print(f"  period {sp} ({game_day}): {len(rows)} lines so far", file=sys.stderr)
    print(f"  projected usage recovered for {len(usg_proj)} players", file=sys.stderr)
    return rows, latest, usg_proj, injury


def main():
    rows, latest, usg_proj, injury = collect()
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

    # Team possessions turn the usage proxy into a real USG%. The per-game scale factor
    # is 100*(team minutes/5)/team shot equivalents; a player's own mean of it converts
    # his *projected* per-minute volume onto the pace he actually plays at.
    ctx = team_context({r["game_id"] for r in rows})
    k_by_player = {}
    for r in rows:
        tc = ctx.get((r["game_id"], r["player"]))
        r["k"] = 100 * (tc[0] / 5) / tc[1] if tc and tc[1] else None
        if r["k"]:
            k_by_player.setdefault(r["player"], []).append(r["k"])
    k_mean = {n: sum(v) / len(v) for n, v in k_by_player.items()}
    print(f"team context resolved for {len(k_mean)} players "
          f"({sum(1 for r in rows if r['k'])}/{len(rows)} lines)", file=sys.stderr)

    for r in rows:
        if r.get("expected") is None:
            r["z"], r["grade"], r["min_grade"] = None, "DNP", "DNP"
            r["usg"] = r["usg_proj"] = r["usg_ratio"] = None
            r["usg_grade"] = "DNP"
            continue
        r["z"] = r["scaled"] / sd
        r["grade"] = band(r["z"], BANDS)
        pm = proj[r["player"]][1]
        r["min_ratio"] = r["min"] / pm
        r["min_grade"] = band(r["min_ratio"], MIN_BANDS)
        # Usage is the third axis: share of the team's possessions, against the player's
        # own projected share. Falls back to the unscaled proxy if the box score is missing.
        up, k = usg_proj.get(r["player"]), r["k"] or k_mean.get(r["player"])
        if up and up > 0 and k:
            r["usg"] = r["shot_eq"] / r["min"] * k
            r["usg_proj"] = up * k_mean.get(r["player"], k)
            r["usg_ratio"] = r["usg"] / r["usg_proj"]
            r["usg_grade"] = band(r["usg_ratio"], USG_BANDS)
        else:
            r["usg"] = r["usg_proj"] = r["usg_ratio"] = None
            r["usg_grade"] = "—"
        if r["period"] == latest:
            r["grade"] = "PARTIAL"  # today's slate may be mid-flight

    con.executescript("""
        DROP TABLE IF EXISTS game_grades;
        CREATE TABLE game_grades(
          player TEXT, fantasy_team TEXT, period INT, date TEXT, game_id TEXT,
          min REAL, fpts REAL, expected REAL, resid REAL, z REAL,
          grade TEXT, min_ratio REAL, min_grade TEXT,
          shot_eq REAL, usg REAL, usg_proj REAL, usg_ratio REAL, usg_grade TEXT);
        CREATE INDEX idx_gg_player ON game_grades(player);
        CREATE INDEX idx_gg_date ON game_grades(date);
    """)
    con.executemany(
        "INSERT INTO game_grades VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [(r["player"], r["fantasy_team"], r["period"], r["date"], r["game_id"],
          round(r["min"], 1), round(r["fpts"], 1),
          None if r.get("expected") is None else round(r["expected"], 1),
          None if r.get("expected") is None else round(r["resid"], 1),
          None if r.get("z") is None else round(r["z"], 2), r["grade"],
          None if r.get("min_ratio") is None else round(r["min_ratio"], 3),
          r["min_grade"], round(r["shot_eq"], 2),
          None if r.get("usg") is None else round(r["usg"], 1),
          None if r.get("usg_proj") is None else round(r["usg_proj"], 1),
          None if r.get("usg_ratio") is None else round(r["usg_ratio"], 3),
          r["usg_grade"]) for r in rows])

    # Per-player form, from completed games only, with the rate/role split kept separate.
    con.executescript("""
        DROP TABLE IF EXISTS player_form;
        CREATE TABLE player_form(
          player TEXT PRIMARY KEY, fantasy_team TEXT, games INT, fpts_pg REAL,
          expected_pg REAL, form_z REAL, min_ratio REAL,
          usg_pct REAL, usg_proj REAL, usg_ratio REAL, injury TEXT,
          best TEXT, worst TEXT, grades TEXT, signal TEXT, note TEXT);
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
        urs = [g["usg_ratio"] for g in gs if g.get("usg_ratio")]
        ur = sum(urs) / len(urs) if urs else 1.0
        ups = [g["usg"] for g in gs if g.get("usg")]
        upct = sum(ups) / len(ups) if ups else None
        upj = next((g["usg_proj"] for g in gs if g.get("usg_proj")), None)
        # Signal: minutes, rate and usage are three different trades. Rate regresses on
        # its own; minutes are the coach's to give; touches are the coach's to take away.
        if fz >= 0.6 and mr >= 1.10:
            sig, note = "SELL HIGH", "beating own rate AND on inflated minutes — both regress"
        elif fz >= 0.6 and ur >= 1.15:
            sig, note = "SELL HIGH (usage)", "rate rides inflated touches, not minutes"
        elif fz >= 0.6:
            sig, note = "SELL HIGH (rate)", "rate above own level; minutes and touches normal"
        elif mr >= 1.15 and fz > -0.3:
            sig, note = "SELL HIGH (minutes)", "production is borrowed minutes, not rate"
        elif fz <= -0.6 and mr >= 0.90 and ur >= 0.90:
            sig, note = "BUY LOW", "rate down, role AND touches intact — the fixable kind"
        elif fz <= -0.6 and mr >= 0.90:
            sig, note = "FADE (usage)", "minutes held but touches gone — not variance"
        elif fz <= -0.6:
            sig, note = "AVOID", "rate down AND minutes down — role problem, not variance"
        elif ur >= 1.20:
            sig, note = "BUY (usage up)", "touches climbing ahead of the box score"
        else:
            sig, note = "HOLD", "within noise of own expectation"
        # Injury is not a fourth axis — it is the confounder that makes the other three
        # unreadable. A hurt player shows rate down with role and touches intact, which
        # is exactly the BUY LOW signature, but the rate does not regress while he is
        # hurt. Flag it rather than trusting the signal.
        inj = injury.get(name, "ACTIVE")
        if inj != "ACTIVE":
            note = f"{note}  ⚠ {inj}: injury confounds all three axes — verify before acting"
        form.append((name, gs[0]["fantasy_team"], len(gs),
                     round(sum(g["fpts"] for g in gs) / len(gs), 1),
                     round(sum(g["expected"] for g in gs) / len(gs), 1),
                     round(fz, 2), round(mr, 3),
                     None if upct is None else round(upct, 1),
                     None if upj is None else round(upj, 1), round(ur, 3), inj,
                     max(gs, key=lambda x: x["z"])["grade"],
                     min(gs, key=lambda x: x["z"])["grade"],
                     " ".join(g["grade"][0] + ("+" if g["z"] >= 1.5 else "") for g in gs),
                     sig, note))
    con.executemany("INSERT INTO player_form VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", form)
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
