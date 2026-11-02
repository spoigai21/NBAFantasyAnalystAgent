#!/usr/bin/env python3
"""Cache every rostered player's ESPN stat lines into league.db, so a player
question is a DB read instead of a live API round-trip.

WHY THIS EXISTS: answering "what's going on with X" used to mean one ad-hoc
script per player hitting mRoster and re-deriving appliedStats by hand. That is
slow, costs an API call, and the derivation got retyped (and mistyped) each time.
Here it is computed once for everyone and stored.

Two tables, long format so a season-over-season diff is plain SQL:
  stat_lines(player, season, src, gp, min, applied_total, applied_avg)
  stat_items(player, season, src, cat, raw_pg, applied_pg)
    src 0 = actual, 1 = ESPN projection.  cat is the label, not the raw id.

The per-unit weights in rule 17 are ESPN's own, read off appliedStats; nothing
here hand-computes a score. Rebuild:
    . ~/.espn-fantasy.env && python3 fantasy/build_stats.py
"""
import sqlite3, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from espn_api import fetch

# category id -> label. Ids verified against ESPN's own per-unit weights, 31 Oct 2026.
CAT = {0:'PTS', 1:'BLK', 2:'STL', 3:'AST', 4:'OREB', 6:'REB', 7:'EJ', 8:'FF',
       11:'TOV', 13:'FGM', 14:'FGA', 15:'FTM', 16:'FTA', 17:'3PM', 18:'3PA',
       37:'DD', 38:'TD', 39:'QD', 40:'MIN', 41:'DREB', 42:'GP', 43:'TW'}

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "league.db")

def main():
    data = fetch('mRoster', 'mTeam')
    teams = {t['id']: (t.get('name') or t.get('abbrev')) for t in data.get('teams', [])}
    lines, items = [], []
    for t in data.get('teams', []):
        for e in t.get('roster', {}).get('entries', []):
            p = e['playerPoolEntry']['player']
            name = p['fullName']
            for s in p.get('stats', []):
                if s.get('statSplitTypeId') != 0:      # season totals only
                    continue
                src = s.get('statSourceId')
                if src not in (0, 1):
                    continue
                season = s.get('seasonId')
                st = s.get('stats') or {}
                ap = s.get('appliedStats') or {}
                gp = st.get('42') or 0
                if not gp:
                    continue
                lines.append((name, season, src, gp, st.get('40') or 0,
                              s.get('appliedTotal'), s.get('appliedAverage')))
                for k in set(ap) | set(st):
                    lab = CAT.get(int(k))
                    if lab is None:
                        continue
                    items.append((name, season, src, lab,
                                  (st.get(k) or 0) / gp, (ap.get(k) or 0) / gp))
    if not lines:
        sys.exit("no stat lines returned — refusing to touch the tables")

    con = sqlite3.connect(DB)
    con.executescript("""
    DROP TABLE IF EXISTS stat_lines;
    DROP TABLE IF EXISTS stat_items;
    CREATE TABLE stat_lines(player TEXT, season INT, src INT, gp REAL, min REAL,
      applied_total REAL, applied_avg REAL, PRIMARY KEY(player,season,src));
    CREATE TABLE stat_items(player TEXT, season INT, src INT, cat TEXT,
      raw_pg REAL, applied_pg REAL, PRIMARY KEY(player,season,src,cat));
    CREATE INDEX idx_si ON stat_items(player,cat);
    """)
    con.executemany("INSERT OR REPLACE INTO stat_lines VALUES (?,?,?,?,?,?,?)", lines)
    con.executemany("INSERT OR REPLACE INTO stat_items VALUES (?,?,?,?,?,?)", items)
    con.commit()
    print(f"stat_lines {len(lines)}  stat_items {len(items)}  "
          f"players {con.execute('SELECT COUNT(DISTINCT player) FROM stat_lines').fetchone()[0]}")
    con.close()

if __name__ == "__main__":
    main()
