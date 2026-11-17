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

    # ⚠ TWO FORM WINDOWS, not one. The shipped board bands on 7 days (user's call,
    # 15 Nov 2026) but the longer window answers a different question and he asked for
    # it on the site, 16 Nov 2026. Both are a WINDOW ON CURRENT VALUE, never a third
    # value — CLAUDE.md rule 32.
    # add_form() mutates rows in place and only writes form_rank / signal_thin /
    # sig_override_why for the players it actually reaches, so a second pass would
    # INHERIT the first pass's leftovers for anyone who drops out of the new window.
    # Hence the explicit wipe between passes.
    CARRY = ("form", "form_n", "form_rank", "form_gap", "form_rel", "form_mr",
             "form_ur", "form_mins", "form_last", "form_missed", "form_dtd",
             "signal", "signal_thin", "sig_override_why")

    def _snap(rs):
        out = {}
        for r in rs:
            avg = r.get("form")
            out[r["name"]] = {
                "avg": round(avg, 1) if avg is not None else None,
                "games": r.get("form_n") or 0,
                "rank": r.get("form_rank"),
                # vs projection, the same column rankings.md's FORM table prints.
                "vsProj": round(avg - r["projected"], 1) if avg is not None else None,
                "mpg": round(r["form_mins"], 1) if r.get("form_mins") is not None else None,
                "signal": r.get("signal") or "—",
                "sigWhy": r.get("sig_override_why"),
                "thin": bool(r.get("signal_thin")),
            }
        return out

    R.add_form(rows, days=7)
    form7 = _snap(rows)
    for r in rows:
        for k in CARRY:
            r.pop(k, None)
    R.add_form(rows, days=14)
    form14 = _snap(rows)

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
            "smallSample": bool(r.get("small_sample")),
            "noProj": bool(r.get("no_proj")),
            # The two windows the site can switch between. Top-level signal/form/sigWhy
            # stay as the 7-day values so an older app.js against a newer rankings.json
            # still renders instead of going blank.
            "form7": form7.get(r["name"]),
            "form14": form14.get(r["name"]),
            "sigWhy": (form7.get(r["name"]) or {}).get("sigWhy"),
            "signalThin": (form7.get(r["name"]) or {}).get("thin", False),
            "signal": (form7.get(r["name"]) or {}).get("signal") or "—",
            "form": (form7.get(r["name"]) or {}).get("avg"),
            "formGames": (form7.get(r["name"]) or {}).get("games") or 0,
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
        "formWindows": [7, 14],
        "players": players,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=1)
    print(f"wrote {OUT}  ({len(players)} players, "
          f"{payload['manualCount']} manual projections, asof {payload['asof']})")


if __name__ == "__main__":
    main()
