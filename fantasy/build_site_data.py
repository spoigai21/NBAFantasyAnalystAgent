#!/usr/bin/env python3
"""Write site/rankings.json — the data behind the Vercel rankings site.

Frontend-only by design: the site is three static files plus this JSON. There is no API,
no server and no build step, so Vercel just serves `site/` and the page works offline.

Run it after rankings.py, which is what actually computes the two lists:

    . ~/.espn-fantasy.env && python3 fantasy/refresh_players.py \
        && python3 fantasy/rankings.py && python3 fantasy/build_site_data.py

⚠ Uses rankings.py as a library so the site can never disagree with rankings.md — same
load(), same MANUAL_PROJ, same rank() calls. Do not reimplement the formulas here.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rankings as R  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "site", "rankings.json")
MY_TEAM = "The Freaky Alien"


def main():
    roster = R.live_roster()
    # ⚠ The fantasy API's player id IS the ESPN athlete id, verified 15 Nov 2026 against
    # a.espncdn.com headshots (Wembanyama 5104157, Davis 6583 etc all return 200). That is
    # what lets the site show a headshot with no extra lookup and no server.
    rows = R.load(roster)
    R.add_form(rows)
    R.rank(rows, "current")
    R.rank(rows, "projected")
    # rankings.py attaches the outside anchors inside main(); do the same one lookup here
    # rather than importing its CLI. DUNNE is a dict name -> rest-of-season rank.
    for r in rows:
        r["dunne"] = R.DUNNE.get(r["name"])

    players = []
    for r in rows:
        if not r.get("enough"):
            continue
        players.append({
            "id": roster[r["name"]].get("id"),
            "name": r["name"],
            "team": r["fteam"],
            "mine": r["fteam"] == MY_TEAM,
            "gp": r["gp"],
            "mpg": round(r["mpg"], 1),
            "injury": r["injury"],
            "current": round(r["current"], 1),
            "currentRank": r.get("current_rank"),
            "projected": round(r["projected"], 1),
            "projectedRank": r.get("projected_rank"),
            "manual": bool(r.get("manual_proj")),
            # The 14-day form screen: signal plus the window it was measured over.
            # Persistence rates for each label are in CLAUDE.md rule 32.
            "age": r.get("age"),
            "missed": r.get("missed"),
            "prone": r.get("prone"),
            "rested": r.get("rested"),
            "sigWhy": r.get("sig_override_why"),
            "smallSample": bool(r.get("small_sample")),
            "signal": r.get("signal") or "—",
            "form": round(r["form"], 1) if r.get("form") is not None else None,
            "formGames": r.get("form_n") or 0,
            "dunne": r.get("dunne"),
        })

    payload = {
        "asof": datetime.date.today().isoformat(),
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "league": "LeFantasy",
        "myTeam": MY_TEAM,
        "minGp": R.MIN_GP,
        "kProj": R.K_PROJ,
        "wPrior": R.W_PRIOR,
        "manualCount": sum(1 for p in players if p["manual"]),
        "players": players,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=1)
    print(f"wrote {OUT}  ({len(players)} players, "
          f"{payload['manualCount']} manual projections, asof {payload['asof']})")


if __name__ == "__main__":
    main()
