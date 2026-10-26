#!/usr/bin/env python3
"""Index EVERY word Josh Lloyd has said into fantasy/league.db, newest first.

Builds two tables:
  lloyd_segments  every passage from every transcript, with show_date + ordinal
  lloyd_fts       FTS5 full-text index over those passages

Nothing is filtered or scored here — this is the complete record, so a claim can
always be checked against the actual words. Rebuild: python3 fantasy/index_lloyd.py
"""
import sqlite3, glob, os, re, sys

DB = "fantasy/league.db"
con = sqlite3.connect(DB)
con.executescript("""
DROP TABLE IF EXISTS lloyd_segments;
DROP TABLE IF EXISTS lloyd_fts;
CREATE TABLE lloyd_segments(
  id INTEGER PRIMARY KEY, show_date TEXT, source_file TEXT, kind TEXT,
  ordinal INT, chapter TEXT, text TEXT);
CREATE VIRTUAL TABLE lloyd_fts USING fts5(
  text, show_date UNINDEXED, source_file UNINDEXED, chapter UNINDEXED,
  content='lloyd_segments', content_rowid='id');
CREATE INDEX idx_seg_date ON lloyd_segments(show_date DESC);
""")

def kind_of(fn):
    for k in ('preview', 'recap', 'mailbag', 'draft-guide', 'bust', 'ranks', 'friday'):
        if k in fn: return k
    return 'other'

rows = []
# newest file first so ordinal/id order already reflects recency
for f in sorted(glob.glob("fantasy/transcripts/*.txt"), reverse=True):
    fn = os.path.basename(f)
    date = fn[:10]
    raw = open(f, errors="replace").read()
    # strip the auto-caption timestamp noise, keep the words
    txt = re.sub(r'\d+:\d+\s*\d*\s*(seconds?|minutes?,?\s*\d*\s*seconds?|minute)?', ' ', raw)
    txt = re.sub(r'[ \t]+', ' ', txt)
    chapter = ''
    # split into passages on chapter markers and sentence runs
    parts = re.split(r'(Chapter \d+[^\n.]{0,90})', txt)
    buf, n = [], 0
    def flush(chap):
        global n
        body = " ".join(" ".join(buf).split())
        buf.clear()
        if len(body) < 40: return
        # chunk to ~700 chars on sentence boundaries so passages stay quotable
        cur = ""
        for sent in re.split(r'(?<=[.?!])\s+', body):
            if len(cur) + len(sent) > 700 and cur:
                globals()['n'] += 1
                rows.append((date, fn, kind_of(fn), globals()['n'], chap, cur.strip()))
                cur = ""
            cur += sent + " "
        if cur.strip():
            globals()['n'] += 1
            rows.append((date, fn, kind_of(fn), globals()['n'], chap, cur.strip()))
    for p in parts:
        if p.startswith('Chapter '):
            flush(chapter); chapter = p.strip()
        else:
            buf.append(p)
    flush(chapter)

con.executemany(
    "INSERT INTO lloyd_segments(show_date,source_file,kind,ordinal,chapter,text) VALUES (?,?,?,?,?,?)", rows)
con.execute("INSERT INTO lloyd_fts(lloyd_fts) VALUES('rebuild')")
con.commit()
tot = con.execute("SELECT COUNT(*) FROM lloyd_segments").fetchone()[0]
words = con.execute("SELECT SUM(LENGTH(text)-LENGTH(REPLACE(text,' ',''))+1) FROM lloyd_segments").fetchone()[0]
print(f"indexed {tot} passages, ~{words:,} words, newest first")
for r in con.execute("SELECT show_date, kind, COUNT(*) c FROM lloyd_segments GROUP BY 1,2 ORDER BY 1 DESC"):
    print(f"   {r[0]}  {r[1]:<12}{r[2]:>5} passages")
con.close()
