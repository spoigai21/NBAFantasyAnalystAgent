#!/usr/bin/env python3
"""Build fantasy/league.db — the queryable store for this league.

Tables
  players        one row per rostered player: value, rates, projection, delta
  lloyd_quotes   every substantive transcript mention, scored, many per player
  game_log       my per-game box scores with applied fantasy points
  transactions   full league transaction history incl. trade contents
  research       my own written findings, keyed by player or topic

Rebuild:  python3 fantasy/build_db.py
"""
import json, re, glob, os, sqlite3, csv, datetime, collections, sys

# Default to the repo copy, not a session scratchpad. The old default pointed at a
# scratchpad dir with no producer in the repo, so this script became unrunnable the
# moment that session ended -- and since it DROPs before reading, running it emptied
# five tables and crashed. Produce the input with: python3 fantasy/refresh_players.py
SCRATCH = sys.argv[1] if len(sys.argv) > 1 else "fantasy"
DB = "fantasy/league.db"

# ---- PRE-FLIGHT: never DROP a table before every input is known to be readable. ----
REQUIRED = [f"{SCRATCH}/dossier_rows.json", "fantasy/game-log.csv"]
missing = [f for f in REQUIRED if not os.path.exists(f)]
if missing:
    sys.exit("build_db.py aborted BEFORE touching the database; nothing was dropped.\n"
             "  missing input(s): " + ", ".join(missing) + "\n"
             "  dossier_rows.json is produced by:  python3 fantasy/refresh_players.py\n"
             "  (that script also refreshes `players` in place, which is usually all\n"
             "   you need -- build_db.py is only required to rebuild lloyd_quotes,\n"
             "   game_log and transactions from the files on disk.)")
if not os.path.exists("fantasy/transcripts") or not glob.glob("fantasy/transcripts/*.txt"):
    sys.exit("build_db.py aborted BEFORE touching the database; nothing was dropped.\n"
             "  fantasy/transcripts/*.txt is empty -- rebuilding would wipe lloyd_quotes.")

# ---- Parse every input UP FRONT. The pre-flight existence check was not enough: on
# 1 Nov 2026 the players INSERT failed on a column-count mismatch AFTER the DROPs had
# already run, emptying lloyd_quotes, game_log and transactions a second time. Existence
# is not readability, and executescript() issues an implicit COMMIT so the DROPs cannot
# be rolled back. So: load and parse first, destroy second.
rows = json.load(open(f"{SCRATCH}/dossier_rows.json"))
if not isinstance(rows, list) or not rows:
    sys.exit("dossier_rows.json is empty or not a list; nothing was dropped.")
_gl = list(csv.DictReader(open('fantasy/game-log.csv')))
_tx = (list(csv.DictReader(open('fantasy/transactions-log.csv')))
       if os.path.exists('fantasy/transactions-log.csv') else [])
_tr = sorted(glob.glob("fantasy/transcripts/*.txt"), reverse=True)
_tr_text = {f: open(f, errors="replace").read() for f in _tr}
print(f"inputs parsed: {len(rows)} players, {len(_gl)} game-log rows, "
      f"{len(_tx)} transactions, {len(_tr)} transcripts")

con = sqlite3.connect(DB)
# Lloyd's words live in a separate, gitignored db — his content, not ours to ship.
con.execute("ATTACH DATABASE 'fantasy/lloyd.db' AS lloyddb")
con.executescript("""
DROP TABLE IF EXISTS lloyddb.lloyd_quotes;
DROP TABLE IF EXISTS game_log;
DROP TABLE IF EXISTS transactions;
CREATE TABLE IF NOT EXISTS players(
  name TEXT PRIMARY KEY, fantasy_team TEXT, nba_team TEXT, status TEXT,
  gp INT, total REAL, per_game REAL, mpg REAL, pts_per_min REAL,
  proj_base REAL, measured_bonus REAL, proj_full REAL, proj_mpg REAL,
  bonus_sample_gp INT, delta REAL);
CREATE TABLE lloyddb.lloyd_quotes(
  player TEXT, show_date TEXT, score INT, quote TEXT, source_file TEXT);
CREATE TABLE game_log(
  date TEXT, player TEXT, pro_team TEXT, opp TEXT, result TEXT, min INT,
  fgm INT, fga INT, ftm INT, fta INT, tpm INT, oreb INT, reb INT, ast INT,
  stl INT, blk INT, tov INT, pts INT, fpts REAL);
CREATE TABLE transactions(
  dt TEXT, sp INT, type TEXT, status TEXT, acting_team TEXT,
  item_type TEXT, player TEXT, from_team TEXT, to_team TEXT, txid TEXT);
CREATE TABLE IF NOT EXISTS research(
  player TEXT, topic TEXT, asof TEXT, finding TEXT, source TEXT);
CREATE INDEX lloyddb.idx_q ON lloyd_quotes(player);
CREATE INDEX idx_g ON game_log(player);
CREATE INDEX IF NOT EXISTS idx_r ON research(player);
""")

# ---------------- players ----------------
# UPSERT, no DROP: a player who was dropped from a roster still has rows in
# game_grades and research that are easier to read with his name resolvable.
# None-safe throughout -- a player with 0 GP has no avg/mpg/ppm yet.
rnd = lambda v, n: None if v is None else round(v, n)
for r in rows:
    # ON CONFLICT, not INSERT OR REPLACE: REPLACE deletes the whole row and re-inserts
    # it, so any column this statement does not name is silently reset to NULL. On
    # 1 Nov 2026 that wiped proj_adj/delta_adj (rule 28) on 130 of 140 players.
    con.execute("""INSERT INTO players
        (name, fantasy_team, nba_team, status, gp, total, per_game, mpg, pts_per_min,
         proj_base, measured_bonus, proj_full, proj_mpg, bonus_sample_gp, delta)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(name) DO UPDATE SET
          fantasy_team=excluded.fantasy_team, nba_team=excluded.nba_team,
          status=excluded.status, gp=excluded.gp, total=excluded.total,
          per_game=excluded.per_game, mpg=excluded.mpg,
          pts_per_min=excluded.pts_per_min, proj_base=excluded.proj_base,
          measured_bonus=excluded.measured_bonus, proj_full=excluded.proj_full,
          proj_mpg=excluded.proj_mpg, bonus_sample_gp=excluded.bonus_sample_gp,
          delta=excluded.delta""", (
        r['name'], r['team'], r['pro'], r['inj'] or 'ACTIVE', int(r['gp'] or 0),
        rnd(r.get('total'), 1), rnd(r['avg'], 2), rnd(r['mpg'], 1), rnd(r['ppm'], 3),
        rnd(r.get('base'), 2), rnd(r['bonus'], 2), rnd(r['full'], 1),
        rnd(r['projmpg'], 1), int(r.get('hgp') or 0), rnd(r.get('delta'), 1)))

# ---------------- lloyd quotes (ALL good ones, not just the best) ----------------
docs = []
for f in _tr:
    t = re.sub(r'\d+:\d+\s*\d*\s*(seconds?|minutes?,?\s*\d*\s*seconds?)?', '', _tr_text[f])
    t = re.sub(r'Chapter \d+[^.]{0,80}', '', t)
    docs.append((os.path.basename(f)[:10], os.path.basename(f), " ".join(t.split())))

cnt = collections.Counter(r['name'].split()[-1] for r in rows)
AMBIG = {s for s, c in cnt.items() if c > 1} | {
    'Brown','Williams','Johnson','Jones','Smith','White','Wilson','Green','Carter','Harris',
    'Mitchell','Murray','Thompson','Miller','Davis','Young','Walker','Jackson','Robinson',
    'Lee','Hart','Bane','Reed','George','Collins','Holiday','Allen','Mann','Ball','Jerome'}
ALIAS = {
 'Buzelis':['Buzelis','Bazales','Bazala'],'Murray-Boyles':['Murray Boils','Murray Boyles','Murray-Boyles'],
 'Antetokounmpo':['Jiannis','Giannis','Antetokounmpo'],'Wembanyama':['Wembanyama','Wemby','Victoryama'],
 'Jokic':['Jokic','Jokich'],'Doncic':['Luka Donic','Luca Donic','Doncic','Donuch'],
 'Gilgeous-Alexander':['Gilgeous'],'Poeltl':['Poeltl','Purle','Purdle'],'Edey':['Edey','Edy'],
 'Acuff':['Acuff','Akoff','Akuff','Akaf'],'Haliburton':['Haliburton','Hallebertton'],
 'Dybantsa':['Dybantsa','Debansa','Debanser'],'Banchero':['Banchero','Bonero'],
 'Kuminga':['Kuminga','Kaminga'],'Sarr':['Alex Sar','Alexar','Sarr'],'Kessler':['Kessler','Kesler'],
 'Sharpe':['Dron Sharp','Sharpe'],'Hachimura':['Hachimura','Hutchimura','Ruie'],
}
GOOD = re.compile(r'\b(minutes?|usage|fantasy points?|roster|drop|add|hold|start|bench|concern|'
  r'love|like|worried|rank|top \d|points league|efficien|rebounds?|assists?|blocks?|steals?|'
  r'shot|shoot|shots|injur|role|great|terrible|special|expect|numbers|production|playing time|'
  r'good|bad|double|upside|value|stream)\b', re.I)
BAD = re.compile(r'(brought to you by|sponsor|promo|download|subscribe|joshoidfantasy|Michael Bolton|'
  r'double bang|podcast network|Kelshi|FanDuel|Quo )', re.I)

def keys_for(full):
    parts = full.split(); first, sur = parts[0], parts[-1]
    if sur in ALIAS: return ALIAS[sur]
    if sur in AMBIG: return [f"{first} {sur}", f"{first[0]}. {sur}"]
    return [sur]

nq = 0
for r in rows:
    seen = set()
    for date, fname, txt in docs:
        for k in keys_for(r['name']):
            for m in re.finditer(r'[^.]{0,300}\b' + re.escape(k) + r'\b[^.]{0,300}\.', txt, re.I):
                s = re.sub(r'\s+', ' ', m.group(0).strip())
                if len(s) < 70 or BAD.search(s): continue
                score = len(GOOD.findall(s))
                if score < 2: continue
                if len(s) > 500: s = s[:497].rsplit(' ', 1)[0] + '…'
                if s[:90] in seen: continue
                seen.add(s[:90])
                con.execute("INSERT INTO lloyddb.lloyd_quotes VALUES (?,?,?,?,?)", (r['name'], date, score, s, fname))
                nq += 1

# ---------------- game log ----------------
ng = 0
for g in _gl:
    if g.get('fantasy_team') != 'FreakyAlien' or not g.get('fpts'): continue
    I = lambda k: int(g[k]) if (g.get(k) or '').strip().lstrip('-').isdigit() else 0
    con.execute("INSERT INTO game_log VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
        g['date'], g['player'], g['pro_team'], g['opp'], g['result'], I('min'),
        I('fgm'), I('fga'), I('ftm'), I('fta'), I('tpm'), I('oreb'), I('reb'),
        I('ast'), I('stl'), I('blk'), I('tov'), I('pts'), float(g['fpts'])))
    ng += 1

# ---------------- transactions ----------------
nt = 0
if True:
    for t in _tx:
        con.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?)", (
            t['datetime'], int(t['sp']) if t['sp'].isdigit() else None, t['type'], t['status'],
            t['acting_team'], t['item_type'], t['player'], t['from'], t['to'], t['txid']))
        nt += 1

con.commit()
print(f"players {len(rows)} | lloyd_quotes {nq} | game_log {ng} | transactions {nt}")
con.close()
