#!/usr/bin/env python3
"""Age, NBA team games played, and the injury-prone flag — cached to player_meta.json.

Three things the fantasy API does NOT carry, each from a different place:

  AGE          site.web.api.espn.com/.../athletes/<id> — the fantasy player object has
               no date of birth or age at all. One call per player, so it is CACHED and
               only refetched for players we have never seen. An age is stale by at most
               a year, which does not matter for a 35+ cutoff.

  GAMES MISSED the player's own GP subtracted from his NBA TEAM's games played, which
               comes from the team endpoint's record summary ("9-4" -> 13).
               ⚠ This is wrong for a player traded mid-season — he is measured against
               his CURRENT team's game count, not the sum of both. Flagged rather than
               silently fixed, because the fantasy API does not expose a trade date.

  INJURY PRONE a hand-maintained list. See the note on INJURY_PRONE below; nothing goes
               in it that is not either named by the user or documented in this repo.

Usage:  python3 fantasy/player_meta.py        # refresh the cache
Import: from player_meta import load_meta, INJURY_PRONE
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "player_meta.json")

ATHLETE = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/"
ATHLETE_STATS = ATHLETE  # + "<id>/stats"
CURRENT_SEASON = "2026-27"   # excluded from the durability history

# ⚠ DURABILITY RULE, user's call 15 Nov 2026: "look at the games played in the last 2-3
# seasons and determine whether they are injury prone for each player. if it is like
# strictly less than 60 is the average in the last 2-3 seasons then mark as injury prone
# (dont include this season obviously and if its a rookie dont say anything if they are
# a 2nd or 3rd year you can also just ignore it)".
# So: average GP over the last 3 COMPLETED seasons, current season excluded. Under 60 is
# injury prone. A player needs all 3 seasons of history to be assessed at all, which is
# what skips rookies and 2nd/3rd-year players — they are left UNASSESSED, not "durable".
DURABILITY_SEASONS = 3
DURABILITY_GP = 60
# The three completed seasons the rule looks at, by name rather than by "last 3 rows".
DURABILITY_WINDOW = ("2023-24", "2024-25", "2025-26")
TEAM = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/"

# ⚠ HAND-MAINTAINED, AND DELIBERATELY SHORT. "Injury prone" is a claim about a real
# person's medical history, so nothing is added here from memory or vibes. An entry needs
# either (a) the user naming him, or (b) a dated, cited note already in this repo.
# Everything else stays absent — absence means "not assessed", never "durable".
#
#   Paul George, Anthony Davis — user, 15 Nov 2026: "they are injury prone if they are
#     notorious for it like paul george anthony davis."
#   Zach Edey — CLAUDE.md rule 32, citing Rotowire 22 Oct 2026: returning from "two left
#     ankle surgeries earlier this year", with Memphis managing him to ~24 minutes.
#
# To add more, give me the names, or ask me to research a specific player and I will cite
# what I find rather than assert it.
INJURY_PRONE = {
    "Paul George": "Long injury history; user-flagged as notorious.",
    "Anthony Davis": "Long injury history; 20 games played last season.",
    "Zach Edey": "Returning from two left ankle surgeries; minutes being managed.",
    # Added 15 Nov 2026 on the user's instruction: "add kawhi, embiid, zion, curry,
    # lillard as injury prone". Marked user-flagged rather than given a specific medical
    # history, because I am not willing to state a diagnosis or surgery from memory —
    # ask me to research any of these and I will cite what I find.
    "Kawhi Leonard": "User-flagged as injury prone.",
    "Joel Embiid": "User-flagged as injury prone.",
    "Zion Williamson": "User-flagged as injury prone.",
    "Stephen Curry": "User-flagged as injury prone.",
    "Damian Lillard": "User-flagged as injury prone.",
    # user, 15 Nov 2026: "coby white put him as injury due to multiple calf injuries"
    "Coby White": "Multiple calf injuries.",
}

# ⚠ NOT ACTUALLY INJURED. ESPN's OUT flag normally VOIDS the signal — "he is not playing, so there is no role
# to read". That is wrong for a healthy veteran being rested on back-to-backs: the flag
# says OUT, the cause is scheduling, and the role is perfectly readable.
# The same applies to any absence that is not medical at all. Names here keep their
# signal despite an OUT/IR flag, and the reason is shown on the card.
# Hand-maintained and user-driven; I do not infer a cause from a games-missed count,
# because two missed games look identical whether it is a calf strain, a coach resting a
# veteran, or a trade request.
#   Joel Embiid — user, 15 Nov 2026: "embiid just say injury prone dont say hes injured
#     as he missed back to backs."
#   Dejounte Murray — user, 15 Nov 2026: "for dejounte hes not injured say like requested
#     a trade and out until finds a new team in description."
NOT_INJURED = {
    "Joel Embiid": "Missing back-to-backs by design, not injured.",
    "Dejounte Murray": "Requested a trade — out until he finds a new team.",
}

# Backwards-compatible alias; the old name said REST and the list is broader than that.
REST_NOT_INJURED = NOT_INJURED

# ⚠ PER-PLAYER SIGNAL OVERRIDE. The computed label is replaced outright for these names.
# Used where the user knows something the three axes cannot see. Each entry is
# (signal, reason) and the reason is the user's, not mine.
#   Luka Doncic — user, 15 Nov 2026: "i think luka is an exception to this rule and you
#     can say ride for him." He printed SELL HIGH because his minutes (35.8) sit under a
#     projected mpg that was set too high; the gate reads that as "overperforming on
#     fewer minutes", which is the shape that evaporates. At 35.8 minutes a game nothing
#     is actually being taken away from him.
SIGNAL_OVERRIDE = {
    "Luka Doncic": ("RIDE", "Minutes are not actually down — the projected mpg was high."),
}


def _get(url):
    out = subprocess.run(["curl", "-s", "--max-time", "20", url],
                         capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        return {}


def season_games(pid):
    """{season: games played} from ESPN's career averages table, current season excluded.

    ⚠ A traded player has MULTIPLE rows for one season — Anthony Davis's 2024-25 appears
    as 42 (one team), 9 (the other) and 51 (the season total). Taking the MAX per season
    picks the total and never undercounts a trade as an injury.
    """
    d = _get(f"{ATHLETE_STATS}{pid}/stats") or {}
    out = {}
    for cat in d.get("categories") or []:
        if cat.get("name") != "averages":
            continue
        labels = cat.get("names") or cat.get("labels") or []
        try:
            gp_i = labels.index("gamesPlayed")
        except ValueError:
            continue
        for st in cat.get("statistics") or []:
            season = (st.get("season") or {}).get("displayName")
            vals = st.get("stats") or []
            if not season or season == CURRENT_SEASON or gp_i >= len(vals):
                continue
            try:
                gp = int(float(vals[gp_i]))
            except (TypeError, ValueError):
                continue
            out[season] = max(out.get(season, 0), gp)
    return out


def durability(seasons):
    """(verdict, detail). verdict is True/False/None — None means NOT ASSESSED.

    ⚠ A season the player missed ENTIRELY has no row in ESPN's table, so averaging "the
    last three rows" silently skips it and makes the most injured players look healthier.
    Kyrie Irving is the case: his three most recent rows are 2022-23, 2023-24 and
    2024-25, because 2025-26 is simply absent.
    So the window is three NAMED seasons, and a missing one counts as 0 — but only for a
    player who was already in the league before the window, which is how a rookie or a
    2nd/3rd-year player stays UNASSESSED rather than being scored as a zero.
    """
    if not seasons:
        return None, None
    was_in_league = any(s < DURABILITY_WINDOW[0] for s in seasons)
    filled = [(s, seasons.get(s, 0)) for s in DURABILITY_WINDOW]
    known = [g for _, g in filled if _ in seasons]
    if not was_in_league and len(known) < DURABILITY_SEASONS:
        return None, None
    avg = sum(g for _, g in filled) / len(filled)
    detail = ", ".join(f"{s} {g}" + ("" if s in seasons else " (missed)") for s, g in filled)
    return avg < DURABILITY_GP, f"{avg:.0f} games a season ({detail})."


def load_meta():
    if os.path.exists(CACHE):
        with open(CACHE) as f:
            return json.load(f)
    return {"ages": {}, "teamGames": {}}


def refresh(player_ids_by_name, pro_team_ids):
    """player_ids_by_name: {name: espn_athlete_id}. pro_team_ids: iterable of team ids."""
    meta = load_meta()
    ages = meta.setdefault("ages", {})

    missing = {n: i for n, i in player_ids_by_name.items()
               if i and str(i) not in ages}
    for n, pid in missing.items():
        a = (_get(f"{ATHLETE}{pid}") or {}).get("athlete", {}).get("age")
        if a:
            ages[str(pid)] = a
    print(f"ages: {len(ages)} cached ({len(missing)} fetched this run)")

    # Season-by-season games played, for the durability rule. Cached like ages.
    hist = meta.setdefault("seasonGames", {})
    need = {n: i for n, i in player_ids_by_name.items() if i and str(i) not in hist}
    for n, pid in need.items():
        hist[str(pid)] = season_games(pid)
    print(f"season histories: {len(hist)} cached ({len(need)} fetched this run)")

    team_games = {}
    for tid in sorted(set(pro_team_ids)):
        t = (_get(f"{TEAM}{tid}") or {}).get("team", {})
        items = (t.get("record") or {}).get("items") or []
        summary = items[0].get("summary") if items else None
        if summary and "-" in summary:
            w, l = summary.split("-")[:2]
            try:
                team_games[str(tid)] = int(w) + int(l)
            except ValueError:
                pass
    meta["teamGames"] = team_games
    print(f"team games played: {len(team_games)} teams")

    with open(CACHE, "w") as f:
        json.dump(meta, f, indent=1, sort_keys=True)
    print(f"wrote {CACHE}")
    return meta


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    import rankings as R
    roster = R.live_roster()
    refresh({n: v.get("id") for n, v in roster.items()},
            [v.get("pro_team_id") for n, v in roster.items() if v.get("pro_team_id")])
