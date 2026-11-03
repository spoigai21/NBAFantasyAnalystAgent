#!/usr/bin/env python3
"""Cut every transcript into ONE SEGMENT PER PLAYER instead of blind 700-char blocks.

WHY THIS EXISTS. index_lloyd.py chunks on sentence boundaries at ~700 chars, which is
blind to who Lloyd is talking about. A chunk routinely spans three players, so a search
for player X returns a window whose first half is about Y -- not a cosmetic problem but
the rule-14 failure mode. CLAUDE.md rule 23 records the real instance: my gold set tested
"Buzelis + 30 plus minutes" and that passage is Lloyd talking about GIDDEY, with Buzelis
entering only as "the other guy." I labelled it Buzelis because the chunk held both names.

Lloyd's recap format is strictly player-by-player -- he names a player, says his piece,
names the next -- so the name boundaries ARE the topic boundaries.

THREE THINGS THIS GETS WRONG IF DONE NAIVELY. All three were observed, not imagined:

 1. BARE SURNAMES COLLAPSE DIFFERENT PEOPLE. A first pass auto-added any surname of 5+
    chars, so "Murray" swept Jamal Murray, Keegan Murray and Dejounte Murray into one
    player, and "Thompson" merged Klay, Ausar and Amen. That is a WORSE mislabelling than
    the chunking it was meant to cure. So: CURATED ALIASES ONLY, from name_aliases, with
    hits > 0. A surname is used only when aliases.py lists it explicitly, because that
    file already encodes which ones are safe (it documents why 'Ant ' and 'AD' are out).
    Players whose aliases are all ambiguous are reported at the end rather than guessed.
 2. TIMESTAMP NOISE SURVIVES. These transcripts carry BOTH m:ss and h:mm:ss stamps, and
    the seconds run straight into the next word ("1:17:161 hour, 17 minutes, 16 secondsOh
    yeah"). index_lloyd.py's regex only handled \\d+:\\d+, so h:mm:ss lines came through.
 3. SEGMENTS START MID-SENTENCE. Anchoring at the alias yields "Bazales obviously, but I
    just..." and throws away the lead-in. Back up to the start of that sentence.

Known limits, stated rather than hidden:
  - A name dropped inside someone else's paragraph correctly ends the first segment and
    starts a new one. Both players get a segment; neither is mislabelled.
  - A passing reference ("unlike the Matas Bazalis one") still makes a segment. It is
    marked by a low `ownscore` -- how much of the span is near that player's own mentions.
  - A segment is a SPAN, not a sentence. lloyd_segments remains the complete record and
    the ONLY thing a quote should be checked against. These are an index.

Rebuild: python3 fantasy/aliases.py && python3 fantasy/split_players.py
"""
import sqlite3, glob, os, re

MIN_LEN = 60
# Lloyd's per-player blurb is ~300-800 chars. A cap is REQUIRED: only tracked players
# create boundaries, so text about an untracked player accrues to the previous one. The
# uncapped first run gave a 1,723-char mean and a 10,557-char "Dejounte Murray" that had
# swallowed the whole Pelicans-Grizzlies section -- the cramming this script exists to stop.
SPAN = 820

con = sqlite3.connect("fantasy/lloyd.db")
con.execute("ATTACH DATABASE 'fantasy/league.db' AS lg")

alias_of, per_player = {}, {}
for player, alias in con.execute(
        "SELECT player, alias FROM lg.name_aliases WHERE hits > 0"):
    alias_of.setdefault(alias.lower(), player)
    per_player.setdefault(player, []).append(alias)
missing = [p for (p,) in con.execute("SELECT DISTINCT player FROM lg.name_aliases")
           if p not in per_player]

pat = re.compile(r'\b(' + '|'.join(re.escape(a) for a in
                 sorted(alias_of, key=len, reverse=True)) + r')\b', re.I)
# h:mm:ss and m:ss, with the glued "NN seconds"/"N minutes, N seconds" tail
TS = re.compile(r'\d{1,2}:\d{2}(?::\d{2})?\s*\d*\s*'
                r'(?:hour[s]?,?\s*\d*\s*)?(?:minute[s]?,?\s*\d*\s*)?(?:second[s]?)?',
                re.I)
# Chapter headings sit on their OWN LINE. Matching them with a regex over the whole
# text cut them mid-title and left the tail in the body, so "Murray-Boyles turns a
# corner" -- Lloyd's HEADING, not his speech -- appeared inside a quotable segment.
# That is an attribution risk, not a cosmetic one. Split line-wise instead.
CHAP_LINE = re.compile(r'^\s*Chapter \d+\b.*$')

con.executescript("""
DROP TABLE IF EXISTS lloyd_player_notes;
DROP TABLE IF EXISTS lpn_fts;
CREATE TABLE lloyd_player_notes(
  id INTEGER PRIMARY KEY, player TEXT, show_date TEXT, source_file TEXT, kind TEXT,
  chapter TEXT, matched TEXT, nchars INT, ownscore REAL, text TEXT);
CREATE VIRTUAL TABLE lpn_fts USING fts5(
  text, player UNINDEXED, show_date UNINDEXED, chapter UNINDEXED,
  content='lloyd_player_notes', content_rowid='id');
CREATE INDEX idx_lpn ON lloyd_player_notes(player, show_date DESC);
""")

def kind_of(fn):
    for k in ('preview','recap','mailbag','draft-guide','buy-low','bust','ranks','friday'):
        if k in fn: return k
    return 'other'

out = []
for f in sorted(glob.glob("fantasy/transcripts/*.txt"), reverse=True):
    fn, date = os.path.basename(f), os.path.basename(f)[:10]
    raw = open(f, errors="replace").read()
    raw = "\n".join(l for l in raw.split("\n") if not l.lstrip().startswith("#"))

    # pull chapter heading LINES out of the body, recording where each one began in
    # the CLEANED string so the label is exact rather than proportionally guessed
    chap_at, parts, n = [], [], 0
    for line in raw.split("\n"):
        if CHAP_LINE.match(line):
            chap_at.append((n, line.strip()))
            continue
        clean = re.sub(r'\s+', ' ', TS.sub(' ', line)).strip()
        if clean:
            parts.append(clean)
            n += len(clean) + 1
    txt = " ".join(parts)
    def chapter_for(p):
        c = ''
        for q, name in chap_at:
            if q <= p: c = name
            else: break
        return c

    hits = []
    for m in pat.finditer(txt):
        who = alias_of[m.group(1).lower()]
        if hits and hits[-1][0] == who:
            hits[-1][3].append(m.start())      # same player again: extend, don't split
            continue
        hits.append([who, m.start(), m.group(1), [m.start()]])

    for i, (who, start, matched, mentions) in enumerate(hits):
        end = hits[i + 1][1] if i + 1 < len(hits) else len(txt)
        lo = start
        back = txt.rfind('. ', max(0, start - 260), start)   # start of HIS sentence
        if back != -1:
            lo = back + 2
        body = txt[lo:end].strip()
        if len(body) > SPAN:
            cut = body[:SPAN]
            br = max(cut.rfind('. '), cut.rfind('? '), cut.rfind('! '))
            body = (cut[:br + 1] if br > MIN_LEN else cut).strip()
        if len(body) < MIN_LEN:
            continue
        # how much of the span sits near his own mentions -- low = passing reference
        span_end = lo + len(body)
        own = sum(1 for p in mentions if lo <= p < span_end)
        others = sum(1 for h in hits if h[0] != who and lo <= h[1] < span_end)
        out.append((who, date, fn, kind_of(fn), chapter_for(start), matched,
                    len(body), round(own / (own + others), 2), body))

con.executemany("INSERT INTO lloyd_player_notes"
                "(player,show_date,source_file,kind,chapter,matched,nchars,ownscore,text)"
                " VALUES (?,?,?,?,?,?,?,?,?)", out)
con.execute("INSERT INTO lpn_fts(lpn_fts) VALUES('rebuild')")
con.commit()

n = con.execute("SELECT COUNT(*) FROM lloyd_player_notes").fetchone()[0]
avg = con.execute("SELECT AVG(nchars) FROM lloyd_player_notes").fetchone()[0]
seg = con.execute("SELECT COUNT(*), AVG(LENGTH(text)) FROM lloyd_segments").fetchone()
print(f"{n} player-attributed notes, mean {avg:.0f} chars   "
      f"(vs {seg[0]} blind chunks, mean {seg[1]:.0f})")
print(f"leftover timestamp noise: "
      f"{con.execute(chr(83)+'ELECT COUNT(*) FROM lloyd_player_notes WHERE text LIKE ?', ('%seconds%',)).fetchone()[0]} notes")
if missing:
    print(f"\n⚠ {len(missing)} tracked players have NO alias that occurs -- not segmented, "
          f"add one to aliases.py if they matter:\n   " + ", ".join(sorted(missing)))
print("\nnewest show, by player:")
d = con.execute("SELECT MAX(show_date) FROM lloyd_player_notes").fetchone()[0]
for r in con.execute("SELECT player, COUNT(*) c, SUM(nchars) s, MAX(ownscore) o "
                     "FROM lloyd_player_notes WHERE show_date=? "
                     "GROUP BY 1 ORDER BY s DESC LIMIT 10", (d,)):
    print(f"   {r[0]:<26}{r[1]:>3} notes {r[2]:>6} chars  best ownscore {r[3]}")
con.close()
