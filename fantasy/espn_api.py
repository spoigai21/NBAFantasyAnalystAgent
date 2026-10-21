#!/usr/bin/env python3
"""Read the LeFantasy league from ESPN's fantasy API.

Needs two cookies from a signed-in browser, supplied as environment variables:
    ESPN_S2   the espn_s2 cookie
    ESPN_SWID the SWID cookie, braces included: {XXXXXXXX-....}

These are account credentials. Keep them out of this repo and out of git.
Put them in ~/.espn-fantasy.env (chmod 600) and source it before running.

Usage:
    python3 fantasy/espn_api.py views            # league settings + teams
    python3 fantasy/espn_api.py roster           # my roster with applied scoring
    python3 fantasy/espn_api.py scoreboard       # all nine matchups
    python3 fantasy/espn_api.py raw mTeam mRoster  # any views, prints JSON
"""
import json, os, subprocess, sys

LEAGUE = "1858125890"
SEASON = "2027"
MY_TEAM = 6
BASE = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/fba/seasons/{SEASON}/segments/0/leagues/{LEAGUE}"


def fetch(*views):
    """Fetch via curl — this Python's urllib has no working CA bundle on macOS."""
    s2, swid = os.environ.get("ESPN_S2"), os.environ.get("ESPN_SWID")
    if not s2 or not swid:
        sys.exit("ESPN_S2 and ESPN_SWID are not set. See the docstring in this file.")
    url = BASE + "?" + "&".join(f"view={v}" for v in views)
    out = subprocess.run(
        ["curl", "-s", "-w", "\\n%{http_code}", url,
         "-H", f"cookie: espn_s2={s2}; SWID={swid}",
         "-H", "accept: application/json", "--max-time", "25"],
        capture_output=True, text=True).stdout
    body, _, code = out.rpartition("\n")
    if code.strip() != "200":
        sys.exit("401 — cookies rejected; they expire, grab fresh ones."
                 if code.strip() == "401" else f"HTTP {code.strip()}")
    return json.loads(body)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "views"
    if cmd == "raw":
        print(json.dumps(fetch(*sys.argv[2:] or ["mTeam"]), indent=2)); return
    if cmd == "views":
        d = fetch("mTeam", "mSettings")
        st = d.get("settings", {})
        print(f"{st.get('name')}  ({len(d.get('teams', []))} teams)\n")
        for t in d.get("teams", []):
            print(f"  id {t['id']:>2}  {t.get('name') or t.get('abbrev'):<34}"
                  f"{t.get('record', {}).get('overall', {}).get('wins', 0)}-"
                  f"{t.get('record', {}).get('overall', {}).get('losses', 0)}")
        return
    if cmd == "roster":
        d = fetch("mRoster", "mTeam")
        for t in d.get("teams", []):
            if t["id"] != MY_TEAM:
                continue
            print(f"{t.get('name')}\n")
            for e in t.get("roster", {}).get("entries", []):
                p = e.get("playerPoolEntry", {}).get("player", {})
                applied = e.get("playerPoolEntry", {}).get("appliedStatTotal")
                print(f"  {p.get('fullName','?'):<26}"
                      f"{'' if applied is None else format(applied, '7.1f')}")
        return
    if cmd == "scoreboard":
        d = fetch("mMatchupScore", "mTeam")
        names = {t["id"]: (t.get("name") or t.get("abbrev")) for t in d.get("teams", [])}
        period = max((m.get("matchupPeriodId", 0) for m in d.get("schedule", [])), default=0)
        for m in d.get("schedule", []):
            if m.get("matchupPeriodId") != 1:
                continue
            h, a = m.get("home", {}), m.get("away", {})
            print(f"  {names.get(h.get('teamId'),'?'):<30}{h.get('totalPoints',0):>7.1f}   "
                  f"{names.get(a.get('teamId'),'?'):<30}{a.get('totalPoints',0):>7.1f}")
        return
    sys.exit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
