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

SCRATCH = sys.argv[1] if len(sys.argv) > 1 else "/private/tmp/claude-502/-Users-shayan-Desktop-nba-fantasy-analyst-agent/39edd093-5167-4a79-910a-32b5cd1386ee/scratchpad"
DB = "fantasy/league.db"

con = sqlite3.connect(DB)
con.executescript("""
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS lloyd_quotes;
DROP TABLE IF EXISTS game_log;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS research;
CREATE TABLE players(
  name TEXT PRIMARY KEY, fantasy_team TEXT, nba_team TEXT, status TEXT,
  gp INT, total REAL, per_game REAL, mpg REAL, pts_per_min REAL,
  proj_base REAL, measured_bonus REAL, proj_full REAL, proj_mpg REAL,
  bonus_sample_gp INT, delta REAL);
CREATE TABLE lloyd_quotes(
  player TEXT, show_date TEXT, score INT, quote TEXT, source_file TEXT);
CREATE TABLE game_log(
  date TEXT, player TEXT, pro_team TEXT, opp TEXT, result TEXT, min INT,
  fgm INT, fga INT, ftm INT, fta INT, tpm INT, oreb INT, reb INT, ast INT,
  stl INT, blk INT, tov INT, pts INT, fpts REAL);
CREATE TABLE transactions(
  dt TEXT, sp INT, type TEXT, status TEXT, acting_team TEXT,
  item_type TEXT, player TEXT, from_team TEXT, to_team TEXT, txid TEXT);
CREATE TABLE research(
  player TEXT, topic TEXT, asof TEXT, finding TEXT, source TEXT);
CREATE INDEX idx_q ON lloyd_quotes(player);
CREATE INDEX idx_g ON game_log(player);
CREATE INDEX idx_r ON research(player);
""")

# ---------------- players ----------------
rows = json.load(open(f"{SCRATCH}/dossier_rows.json"))
for r in rows:
    con.execute("INSERT OR REPLACE INTO players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
        r['name'], r['team'], r['pro'], r['inj'] or 'ACTIVE', int(r['gp']),
        round(r['avg']*r['gp'],1), round(r['avg'],2), round(r['mpg'],1), round(r['ppm'],3),
        round((r['full']-r['bonus']),2) if r['full'] else None, round(r['bonus'],2),
        round(r['full'],1) if r['full'] else None, round(r['projmpg'],1),
        int(r.get('hgp') or 0),
        round(r['avg']-r['full'],1) if (r['full'] and r['gp']) else None))

# ---------------- lloyd quotes (ALL good ones, not just the best) ----------------
docs = []
for f in sorted(glob.glob("fantasy/transcripts/*.txt"), reverse=True):
    t = re.sub(r'\d+:\d+\s*\d*\s*(seconds?|minutes?,?\s*\d*\s*seconds?)?', '', open(f, errors="replace").read())
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
                con.execute("INSERT INTO lloyd_quotes VALUES (?,?,?,?,?)", (r['name'], date, score, s, fname))
                nq += 1

# ---------------- game log ----------------
ng = 0
for g in csv.DictReader(open('fantasy/game-log.csv')):
    if g.get('fantasy_team') != 'FreakyAlien' or not g.get('fpts'): continue
    I = lambda k: int(g[k]) if (g.get(k) or '').strip().lstrip('-').isdigit() else 0
    con.execute("INSERT INTO game_log VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
        g['date'], g['player'], g['pro_team'], g['opp'], g['result'], I('min'),
        I('fgm'), I('fga'), I('ftm'), I('fta'), I('tpm'), I('oreb'), I('reb'),
        I('ast'), I('stl'), I('blk'), I('tov'), I('pts'), float(g['fpts'])))
    ng += 1

# ---------------- transactions ----------------
nt = 0
if os.path.exists('fantasy/transactions-log.csv'):
    for t in csv.DictReader(open('fantasy/transactions-log.csv')):
        con.execute("INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?)", (
            t['datetime'], int(t['sp']) if t['sp'].isdigit() else None, t['type'], t['status'],
            t['acting_team'], t['item_type'], t['player'], t['from'], t['to'], t['txid']))
        nt += 1

con.commit()
print(f"players {len(rows)} | lloyd_quotes {nq} | game_log {ng} | transactions {nt}")
con.close()
