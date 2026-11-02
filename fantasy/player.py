#!/usr/bin/env python3
"""ONE command for everything we know about a player. Start here, always.

    ./fantasy/p.sh buzelis            # full picture
    ./fantasy/p.sh "amen" --lloyd 6   # more Lloyd
    ./fantasy/p.sh garland --q "turnovers"   # steer the Lloyd search

WHY: the old sequence was 4-6 separate calls (q.sh for players, q.sh for
game_grades, q.sh for player_form, lloyd.sh, plus an ad-hoc API script to
decompose the scoring) and then reading fantasy/lloyd-daily-notes.md by hand.
That is slow, costs an API call per player, and the notes are a paraphrase of
what is already in the DB. Everything below is a local read.

Sections: WHO / LEVEL / AXES / TREND / SPLIT / LLOYD / OURS.
Nothing here is hand-computed scoring -- SPLIT comes from ESPN's own
appliedStats, cached by fantasy/build_stats.py.
"""
import sqlite3, sys, os, argparse, re

HERE = os.path.dirname(os.path.abspath(__file__))
LEAGUE, LLOYD = os.path.join(HERE, "league.db"), os.path.join(HERE, "lloyd.db")
CUR, PREV = 2027, 2026

def resolve(con, q):
    """Fuzzy-match a name. Exact, then prefix, then substring on any token."""
    for sql, arg in (("SELECT name FROM players WHERE name=? COLLATE NOCASE", q),
                     ("SELECT name FROM players WHERE name LIKE ? COLLATE NOCASE", q + "%"),
                     ("SELECT name FROM players WHERE name LIKE ? COLLATE NOCASE", "%" + q + "%")):
        hits = [r[0] for r in con.execute(sql, (arg,))]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            print(f"ambiguous '{q}': {', '.join(hits)}", file=sys.stderr)
            return hits[0]
    # Fall back to the caption-alias table, so "wemby", "edey", "bales" all land.
    # Without this, the names I actually type are the ones that fail.
    r = con.execute("SELECT player FROM name_aliases WHERE alias LIKE ? COLLATE NOCASE "
                    "ORDER BY hits DESC LIMIT 1", (f"%{q}%",)).fetchone()
    if r:
        got = resolve(con, r[0])
        if got:
            return got
    return None

def bar(v, lo=0.75, hi=1.25):
    """Tiny visual for a ratio so a glance beats reading the number."""
    if v is None: return ""
    n = max(0, min(10, round((v - lo) / (hi - lo) * 10)))
    return "[" + "#" * n + "." * (10 - n) + "]"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name"); ap.add_argument("--lloyd", type=int, default=4)
    ap.add_argument("--q", default=None, help="extra terms to rank Lloyd hits on")
    ap.add_argument("--games", type=int, default=12)
    a = ap.parse_args()

    con = sqlite3.connect(LEAGUE)
    con.row_factory = sqlite3.Row
    name = resolve(con, a.name)
    if not name:
        sys.exit(f"no player matching '{a.name}' in players")

    # ---------- WHO / LEVEL ----------
    p = con.execute("SELECT * FROM players WHERE name=?", (name,)).fetchone()
    f = con.execute("SELECT * FROM player_form WHERE player=?", (name,)).fetchone()
    print(f"\n{'='*78}\nWHO    {name}  |  {p['nba_team']}  |  {p['status']}  |  "
          f"{p['fantasy_team'] or 'free agent'}")

    pa, da = p['proj_adj'], p['delta_adj']
    print(f"LEVEL  {p['per_game']:.1f}/g over {int(p['gp'] or 0)} GP"
          + (f"   vs proj_adj {pa:.1f}  ({da:+.1f})" if pa else "")
          + (f"   [ESPN raw proj {p['proj_full']:.1f}, runs ~9.5% high -- rule 28]" if p['proj_full'] else ""))
    if p['mpg'] and p['proj_mpg']:
        print(f"       {p['mpg']:.1f} mpg vs {p['proj_mpg']:.1f} projected"
              f"   |  {p['per_game']/p['mpg']:.3f} fpts/min")

    # ---------- AXES ----------
    if f:
        print(f"AXES   rate   z {f['form_z']:+.2f}   (vs pure projection = talent)")
        print(f"       mins   {f['min_ratio']:.2f} {bar(f['min_ratio'])}  coach-controlled, does not revert")
        print(f"       usage  {f['usg_ratio']:.2f} {bar(f['usg_ratio'])}  {f['usg_pct']:.1f}% vs {f['usg_proj']:.1f}% proj (20.0 = league avg)")
        print(f"       SIGNAL {f['signal']}   injury {f['injury']}   grades {f['grades']}")
        if f['injury'] not in (None, 'ACTIVE'):
            print("       !! injury invalidates the other three axes -- rule 27")

    # ---------- TREND ----------
    g = con.execute("SELECT date,min,fpts,grade,min_grade,usg,usg_grade FROM game_grades "
                    "WHERE player=? ORDER BY period", (name,)).fetchall()
    if g:
        print(f"TREND  {len(g)} graded: " + " ".join(f"{int(r['fpts'])}" for r in g[-a.games:]))
        print("       mins:    " + " ".join(f"{int(r['min'])}" for r in g[-a.games:]))
        print("       usage%:  " + " ".join(f"{r['usg']:.0f}" if r['usg'] else "--" for r in g[-a.games:]))
        def seg(rows):
            m = sum(r['min'] for r in rows); return (sum(r['fpts'] for r in rows)/len(rows),
                                                     sum(r['fpts'] for r in rows)/m if m else 0)
        if len(g) >= 4:
            k = min(5, max(2, len(g)//2))
            (fe, re_), (fl, rl) = seg(g[:k]), seg(g[-k:])
            print(f"       first {k}: {fe:.1f}/g ({re_:.3f}/min)   last {k}: {fl:.1f}/g ({rl:.3f}/min)"
                  f"   -> {'improving' if rl > re_ else 'declining'} per minute")
        worst = min(g, key=lambda r: r['fpts'])
        if len(g) >= 4 and worst['fpts'] < 0.45 * (p['per_game'] or 1):
            ex = [r for r in g if r is not worst]
            print(f"       !! one outlier ({int(worst['fpts'])} on {worst['date']}) is dragging the mean: "
                  f"without it {sum(r['fpts'] for r in ex)/len(ex):.1f}/g")

    # ---------- SPLIT (ESPN's own appliedStats, cached) ----------
    L = con.execute("SELECT * FROM stat_lines WHERE player=? AND season=? AND src=0", (name, PREV)).fetchone()
    N = con.execute("SELECT * FROM stat_lines WHERE player=? AND season=? AND src=0", (name, CUR)).fetchone()
    if L and N and L['min'] and N['min']:
        mL, mN = L['min']/L['gp'], N['min']/N['gp']
        aL, aN = L['applied_avg'], N['applied_avg']
        rL, rN = aL/mL, aN/mN
        mins_only = aL * mN / mL
        tot = aN - aL
        print(f"SPLIT  vs {PREV-1}-{str(PREV)[2:]} ({int(L['gp'])} GP): {aL:.1f} -> {aN:.1f}/g  ({tot:+.2f})")
        print(f"       per-minute {rL:.3f} -> {rN:.3f}  ({rN/rL-1:+.1%})   "
              f"mpg {mL:.1f} -> {mN:.1f}")
        if abs(tot) > 0.1:
            print(f"       minutes {mins_only-aL:+.2f} ({abs(mins_only-aL)/abs(tot):.0%})  "
                  f"rate {aN-mins_only:+.2f} ({abs(aN-mins_only)/abs(tot):.0%})")
        it = {}
        for r in con.execute("SELECT season,cat,raw_pg,applied_pg FROM stat_items "
                             "WHERE player=? AND src=0 AND season IN (?,?)", (name, PREV, CUR)):
            it.setdefault(r['cat'], {})[r['season']] = (r['raw_pg'], r['applied_pg'])
        mv = sorted(((c, v.get(CUR,(0,0))[1] - v.get(PREV,(0,0))[1],
                      v.get(PREV,(0,0))[0], v.get(CUR,(0,0))[0])
                     for c, v in it.items() if c not in ('MIN','GP','3PA','DREB')),
                    key=lambda x: -abs(x[1]))
        print("       movers (applied/g, raw/g in brackets):")
        for c, d, r0, r1 in mv[:8]:
            if abs(d) < 0.25: break
            print(f"         {c:<5}{d:+7.2f}   ({r0:.2f} -> {r1:.2f})")
        def pct(cat_m, cat_a, s):
            m = it.get(cat_m, {}).get(s, (0,0))[0]; at = it.get(cat_a, {}).get(s, (0,0))[0]
            return (m/at if at else 0), at
        (fL_, faL), (fN_, faN) = pct('FGM','FGA',PREV), pct('FGM','FGA',CUR)
        (tL_, taL), (tN_, taN) = pct('FTM','FTA',PREV), pct('FTM','FTA',CUR)
        print(f"       FG% {fL_:.1%} -> {fN_:.1%} on {faL:.1f} -> {faN:.1f} FGA"
              f"   |  FT% {tL_:.1%} -> {tN_:.1%} on {taL:.1f} -> {taN:.1f} FTA")
    elif N:
        print(f"SPLIT  no {PREV} actuals cached (rookie, or did not play) -- "
              f"compare to projection only")

    # ---------- LLOYD ----------
    if os.path.exists(LLOYD):
        con.execute(f"ATTACH DATABASE '{LLOYD}' AS l")
        als = [r[0] for r in con.execute(
            "SELECT alias FROM name_aliases WHERE hits>0 AND (player=? OR player LIKE ?)",
            (name, f"%{a.name}%"))]
        if not als:
            als = [name.split()[-1]]
        m = " OR ".join(f'"{x}"' for x in als)
        if a.q:
            m = f"({m}) AND ({a.q})"
        print(f"LLOYD  matching {m[:90]}")
        # TWO RANKED PASSES, FULL PASSAGES, DEDUPED. Measured 2 Nov 2026 over 8
        # questions whose answers were verified present in the corpus AND verified
        # to be about that player:
        #   old lloyd.sh (4 date-ordered passages)     5/8 recall, 20,989 chars
        #   bm25 + a 380-char question-centred window  4/8 recall,  4,436 chars
        #   this (2 relevance + 2 recency, full)       7/8 recall, 15,488 chars
        # Windowing LOST recall: a 700-char passage is already a snippet, so
        # compressing it throws away the answer while retrieval was finding the
        # right passage all along. The win comes from RANKING (fewer, better
        # passages), not from trimming them. The two passes miss different things
        # -- relevance surfaces older material that date-ordering buries (Edey's
        # "low 20s", LaVine's "more usage"), recency catches what bm25 ranks down.
        def hits(match, order, k):
            return con.execute(
                "SELECT s.id, s.show_date d, s.kind k, s.text t FROM l.lloyd_fts "
                "JOIN l.lloyd_segments s ON s.id=lloyd_fts.rowid "
                f"WHERE lloyd_fts MATCH ? ORDER BY {order} LIMIT ?", (match, k)).fetchall()
        seen, K = {}, max(1, a.lloyd)
        try:
            if a.q:                                  # pass 1: relevance
                for r in hits(f"({m}) AND ({a.q})", "bm25(lloyd_fts), s.show_date DESC", K):
                    seen[r['id']] = r
            for r in hits(" OR ".join(f'"{x}"' for x in als),   # pass 2: recency
                          "s.show_date DESC, s.ordinal", K):
                seen.setdefault(r['id'], r)
            if not seen:
                print("       NO HITS -- do not attribute anything to him (rule 19)")
            for r in sorted(seen.values(), key=lambda r: r['d'], reverse=True):
                print(f"       [{r['d']} {r['k']}] {' '.join(r['t'].split())}")
        except Exception as e:
            print(f"       FTS error: {e}")

    # ---------- OURS ----------
    rs = con.execute("SELECT asof,topic FROM research WHERE player=? ORDER BY asof DESC, rowid DESC LIMIT 8",
                     (name,)).fetchall()
    if rs:
        print("OURS   our own logged findings (read in full with q.sh):")
        for r in rs:
            print(f"       [{r['asof']}] {r['topic']}")
    print('='*78)

if __name__ == "__main__":
    main()
