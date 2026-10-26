#!/usr/bin/env python3
"""Pre-claim checks. Run the relevant one BEFORE stating something, not after.

  python3 fantasy/verify.py quote "correctly off the board"   does Lloyd actually say this?
  python3 fantasy/verify.py score                             live matchup score + is it closed?
  python3 fantasy/verify.py slate [YYYYMMDD]                  are all games final?
  python3 fantasy/verify.py all                               score + today's slate

Exists because on 25 Oct 2026 I (a) attributed a fabricated quote to Lloyd,
(b) reported totalPoints (lags a day) as the score three times, and
(c) filed a third-quarter box score as a final result.
"""
import sqlite3, sys, json, subprocess, os, datetime, re

DB = "fantasy/league.db"
LLOYD_DB = "fantasy/lloyd.db"   # gitignored: Lloyd's transcripts, not ours to redistribute

def quote(s):
    con = sqlite3.connect(DB)
    con.execute(f"ATTACH DATABASE '{LLOYD_DB}' AS lloyddb")
    words = [w for w in re.findall(r"[A-Za-z']+", s) if len(w) > 2]
    exact = con.execute("SELECT COUNT(*) FROM lloyddb.lloyd_fts WHERE lloyd_fts MATCH ?", (f'"{s}"',)).fetchone()[0]
    print(f'exact phrase "{s}"  ->  {exact} hit(s)')
    if exact:
        for r in con.execute("""SELECT s.show_date,s.source_file,s.text FROM lloyddb.lloyd_fts f
              JOIN lloyddb.lloyd_segments s ON s.id=f.rowid WHERE lloyd_fts MATCH ?
              ORDER BY s.show_date DESC LIMIT 3""", (f'"{s}"',)):
            print(f"\n  [{r[0]} {r[1]}]\n  {r[2][:420]}")
        return 0
    print("\n  *** NOT FOUND. Do not attribute this to Lloyd. ***")
    if words:
        loose = " OR ".join(f'"{w}"' for w in words[:6])
        n = con.execute("SELECT COUNT(*) FROM lloyddb.lloyd_fts WHERE lloyd_fts MATCH ?", (loose,)).fetchone()[0]
        print(f"  (loose match on its words: {n} passages — check them before paraphrasing)")
    return 1

def _espn(view):
    s2, swid = os.environ.get("ESPN_S2"), os.environ.get("ESPN_SWID")
    if not s2: sys.exit("source ~/.espn-fantasy.env first")
    url = ("https://lm-api-reads.fantasy.espn.com/apis/v3/games/fba/seasons/2027"
           f"/segments/0/leagues/1858125890?view={view}&view=mTeam")
    return json.loads(subprocess.run(["curl","-s","--max-time","25",url,
        "-H",f"cookie: espn_s2={s2}; SWID={swid}","-H","accept: application/json"],
        capture_output=True,text=True).stdout)

def score():
    d = _espn("mMatchupScore")
    nm = {t['id']:(t.get('name') or t.get('abbrev')) for t in d.get('teams',[])}
    cur = d.get('status',{}).get('currentMatchupPeriod')
    bad = 0
    for m in d.get('schedule',[]):
        if m.get('matchupPeriodId') != cur: continue
        h,a = m.get('home',{}), m.get('away',{})
        if 6 not in (h.get('teamId'), a.get('teamId')): continue
        me,op = (h,a) if h.get('teamId')==6 else (a,h)
        live_me, live_op = me.get('totalPointsLive'), op.get('totalPointsLive')
        stale_me, stale_op = me.get('totalPoints'), op.get('totalPoints')
        print(f"LIVE   {nm[6]}: {live_me}   {nm[op['teamId']]}: {live_op}   "
              f"margin {(live_me or 0)-(live_op or 0):+.0f}")
        print(f"stale  totalPoints says {stale_me} / {stale_op}  <- DO NOT QUOTE THIS")
        print(f"winner = {m.get('winner')}   "
              f"{'-> matchup is STILL OPEN' if m.get('winner')=='UNDECIDED' else '-> settled'}")
        if (live_me or 0) != (stale_me or 0):
            print(f"  ⚠ the two differ by {abs((live_me or 0)-(stale_me or 0)):.0f} — "
                  f"totalPoints is missing the current scoring period")
            bad = 1
    return bad

def slate(date=None):
    date = date or datetime.date.today().strftime("%Y%m%d")
    j = json.loads(subprocess.run(["curl","-s","--max-time","25",
        f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={date}"],
        capture_output=True,text=True).stdout)
    ev = j.get('events',[])
    live = [e for e in ev if e['competitions'][0]['status']['type']['state'] == 'in']
    pre  = [e for e in ev if e['competitions'][0]['status']['type']['state'] == 'pre']
    print(f"{date}: {len(ev)} games — {len(ev)-len(live)-len(pre)} final, {len(live)} in progress, {len(pre)} not started")
    for e in live + pre:
        print(f"   {e['shortName']:<12}{e['competitions'][0]['status']['type']['detail']}")
    if live or pre:
        print("\n  *** Slate incomplete. Any team total you quote now is PARTIAL. ***")
        return 1
    print("  all final — totals are safe to report")
    return 0

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "quote": sys.exit(quote(" ".join(sys.argv[2:])))
    if cmd == "score": sys.exit(score())
    if cmd == "slate": sys.exit(slate(sys.argv[2] if len(sys.argv) > 2 else None))
    rc = score(); print(); rc |= slate(); sys.exit(rc)
