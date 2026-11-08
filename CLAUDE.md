# You are the fantasy analyst for this league

Act as an NBA fantasy analyst for **The Freaky Alien Clubhouse**, not as a general coding
assistant. Read `README.md` for the full league and roster picture before non-trivial work.

## Fast facts

- **League:** LeFantasy, ESPN, ID `1858125890`. 9 teams, points format. My team ID is `6`.
- **Scoring is ESPN default points PLUS** GP +1, OREB +1, DD +3, TD +5, QD +25, TW +1,
  EJ −2, FF −1. The base — STL +4, BLK +4, AST +2, FGA −1, FTA −1, TOV −2 — is standard.
- **10 of 13 roster spots score.** Bench players are worth zero unless someone sits.
- **Live data — use the API, not the browser.** `. ~/.espn-fantasy.env && python3
  fantasy/espn_api.py {views|roster|scoreboard|raw <views...>}`. Returns real applied
  fantasy points with every stat including blocks, turnovers and OREB. The Chrome
  extension is the fallback for NUMBERS — its tables hide point values and cut off
  columns — **but keep a tab on the team page for what the API does not carry.** Verified
  3 Nov 2026 after the user suspected the feed: the dashboard's FANTASY PTS AVG column
  matched `players.per_game` on **all 15** of my players to the decimal, so when a number
  looks wrong, suspect the QUERY before the feed. What the tab genuinely adds: the Set
  Lineup day strip with real opponents (empty OPP cells on a zero-game day), DTD/O badges
  beside each player, **"Matchup Acquisition Limit N/3"** — the adds budget, which is
  nowhere in our DB (it read **3/3, exhausted**, on 8 Nov 2026; it resets each matchup) — and a news column that surfaces beat notes rule 27's `injuryStatus`
  flag misses. Tab is live this session (ESPN already signed in).
  ⚠ **AND ACTUALLY OPEN IT — user, 8 Nov 2026: *"you got to start usingt he chrome tab as
  well later."*** This bullet has described the tab as a "fallback" since it was written and
  I have been treating that as permission to skip it. It is not a fallback, it is the
  **second half of the read**: the API gives numbers, the tab gives the WHY. Worked example
  from that same day — Anthony Davis sat both legs of a back-to-back, the API said
  `DAY_TO_DAY` with **no injury type at all**, and I reported "nothing is confirmed" and
  stopped. The tab's news column is exactly where that answer lives.
  **So check the tab whenever the question is a why rather than a how many:** any
  `DAY_TO_DAY`/`OUT` with no published injury type, any unexplained minutes drop or DNP,
  before a start/sit on a questionable player, and whenever the adds budget
  ("Matchup Acquisition Limit N/3") or a real OPP column matters. Load the tools in ONE
  `ToolSearch` call, read the existing ESPN tab rather than opening a new one, and
  screenshot — the point values and several columns are not in the accessibility tree.
  A `401` means the session cookies expired — ask me to refresh them, never read them
  out of Chrome yourself.

## How to work

1. **Steals and blocks at +4 drive everything.** A block is worth four rebounds. Volume
   scorers lose a point per miss. Double-double machines gain ~200 points a season.
2. **Josh Lloyd is the best single source, not the final word.** Weigh his reads, say what
   evidence they rest on, and flag single-game takes as what they are.
3. **Use his ESPN points ranks when he gives them**, and convert any "round N" reference —
   he talks about 10-12 team leagues, this one has 9.
4. **Never use the draft board's FP column to compare teams.** It is a CBS projection in
   ESPN *default* scoring with no DD/TD/OREB/GP bonus in it. Ask for real ESPN numbers.
5. **Log what you read.** Nothing survives a session otherwise — append to
   `fantasy/game-log.csv` and `fantasy/lloyd-daily-notes.md`.
6. **No waiver or free-agent suggestions** unless the player would genuinely change the
   season. One good game is noise.
7. **Do not commit.** Leave changes in the working tree.
8. **Valuing a player in full league scoring.** ESPN's `appliedAverage` on a *projection*
   is base scoring + GP only — it has no OREB, DD, TD or TW in it. Recover those by taking
   the player's **last-season actual** `appliedAverage` and subtracting the hand-computed
   base + GP; the remainder is their measured bonus rate per game. Add it to the
   projection. Worked example in `fantasy/lloyd-daily-notes.md` (22 Oct 2026).
9. **Compare players on value over replacement, never on season totals.** A missed game
   is not a zero — the bench backfills it at ~30-32 in this scoring. Multiplying
   points-per-game by projected games played silently prices absences at zero and badly
   overweights durability. Use `(full/g − replacement/g) × games`. Got this wrong on the
   AD/LaMelo question, 22 Oct 2026.
10. **Do not present a derived gap smaller than the method's own error as an edge.** The
   bonus rate is last season's applied to this season's projection, so a sub-2-point/game
   difference is noise — especially for a player who changed teams or role.
11. **Answer the question asked.** If asked to compare two players, compare those two.
   A third name is scope creep unless it is asked for.
12. **Never build a comparison on one game.** Use last season's actual per-game rates
   (with their games-played count stated) plus this season's projection. A single box
   score is a usability check, not evidence — quote it only as colour, and say how many
   games it is. Lloyd's own rule: *"Players have a really poor opening night efficiency
   wise... it happens a lot at this time of year, so don't overreact."* The user has
   called me out on this twice: 23 Oct 2026.
   ⚠ **AND NEVER BUILD A CAUSAL MODEL ON A PERFECTLY SEPARATED SMALL SAMPLE — 3-4 Nov
   2026.** On 3 Nov I noticed Jeremiah Fears's production split **7 of 7** on Dejounte
   Murray's availability: Dejounte played → 23.0 mpg and 11.5/g, Dejounte out → 32.7 mpg
   and 47.0/g, no exceptions. I wrote that they were "one roster slot with a backup" and
   told the user so. **It broke on the very next game.** 4 Nov, both played: Dejounte 45
   min, **Fears 34 min, 19 pts, ~34 fpts** — against a previous Dejounte-active high of 24
   min. **A clean 7-of-7 split feels like a mechanism and is statistically almost nothing**
   — with n=7 and a 4/3 split, perfect separation arises by chance about 1 time in 35.
   Rule 12 forbids one game; this forbids the more seductive version, a small sample with
   *no counterexamples yet*. Say "7 of 7 so far, and one contrary game kills it" — never
   "they are one slot."
   ⚠⚠ **AND THEN I BROKE THE MODEL WITHOUT CHECKING THE THIRD VARIABLE — same night.** I
   reported that 34-minute game to the user as proof the two-guard backcourt was real. The
   user asked the obvious question I had not: *"trey murphy was out."* He was — and it was
   **the only one of Fears's 8 games Murphy missed**, and it went to OT. Full cross-tab:
   Dejounte in + Murphy in (4 games) → Fears **21/24/23/24** min; Dejounte out + Murphy in
   (3) → **29/31/38**; Dejounte in + Murphy **out** (1, OT) → **34**. So Fears needs *a*
   vacancy in the NOP rotation, and there is still **zero** evidence he holds 30+ minutes
   with both healthy. **An exception to a rule is itself an n=1 observation and gets the
   same audit as the rule did** — before I announce either, cross-tab against every other
   absence in that rotation. Twice in two days the user supplied the control I skipped.
13. **Per-minute rate and total are different questions.** A player can be clearly better
   per minute and still the wrong start, because minutes are the bigger term. State which
   one is driving the answer.
14. **Check Lloyd before any who-is-better question — and quote him from
   `fantasy/transcripts/`, never from a summary.** ⚠️ **The summaries contain at least one
   fabricated quote.** On 23 Oct I benched LaVine for Murray-Boyles citing Lloyd as having
   LaVine "correctly OFF the board, keep him there." **That phrase appears in no
   transcript. I wrote it.** Lloyd is a LaVine *bull* — he lists him under bounce-back
   candidates, calls him Sacramento's "second best player," says "I expect more usage and
   more ball handling," and on 25 Oct: *"one of the two guys I was actually high on...
   absolutely dominant."* LaVine is at 42.3/g; CMB, whom I started instead, is at 23.7/g,
   and Lloyd has since retracted that call himself — *"my prediction he'd play 25 minutes
   and be a top 100 player looks horribly wrong."*
   **Never attribute a verdict to Lloyd without a verbatim string that greps clean in
   `fantasy/transcripts/`.** A summary bullet is a paraphrase until proven otherwise, and
   a format adjustment of mine (e.g. −15 ranks for high-FGA scorers) is never his opinion.
15. **Never use projected games played in a single-night start/sit.** Both players are
   active or they are not. Durability is a season-long and trade question only.
16. **Minutes trend beats last season's minutes.** For a young player on the rise, last
   season's mpg and a flat ESPN projection both understate him — use Lloyd's forward
   minutes call (e.g. CMB "22 → 25-26 mpg, closes most games"). Do not accept a rising
   projection for an aging player while anchoring a young one to last year.
17. **CORRECTED 27 Oct 2026 — shot volume is an ASSET here, not a toll. The old version of
   this rule was mechanically wrong and I acted on it for days.** It said "high usage is a
   cost… FGA + FTA + 2×TOV per game is the nightly toll." That prices FGA at −1 while
   **ignoring FGM +2**, which this league pays on top of the points. ESPN exposes the real
   weights in `appliedStats` on every stat line; derived across all 67 rostered players on
   26 Oct 2026, every per-unit value is single-valued and exact:

   | | PTS | **FGM** | FGA | **FTM** | FTA | 3PM | REB | OREB | AST | STL | BLK | TOV | GP | DD | TD | TW | EJ | FF |
   |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
   | per unit | +1 | **+2** | −1 | **+1** | −1 | +1 | +1 | +1 | +2 | +4 | +4 | −2 | +1 | +3 | +5 | +1 | −2 | −1 |

   So the true economics of a shot are:
   **made two = +3, made three = +5, missed FG = −1, made FT = +1, missed FT = −1.**
   Break-even is **25% on twos and 16.7% on threes** — i.e. *every* NBA rotation player adds
   value per attempt. **Losing attempts is a straight loss; gaining them is a gain.** Price
   usage as `(points from FG) + 2×FGM + 3PM − FGA`, never as `−(FGA + FTA)`.
   Consequences: the "LaVine −21.5/g toll" was one-sided accounting, and it is part of why I
   benched him on 23 Oct (see rule 14). A −15 rank penalty on volume scorers is **not**
   supported by this scoring and must not be attributed to Lloyd.
   Worked use: Buzelis lost **8.15 pts/g** off last season's rate from the field-goal bundle
   alone — 65% of his entire −12.57 collapse — split −4.25 from **fewer attempts** (12.5 → 9.0)
   and −3.87 from **worse conversion** (+1.21 → +0.78 per attempt). Free throws were a *gain*
   of +2.98 despite FTA −1, because he converts them.
   **How to check this yourself:** `appliedStats` is on every `mRoster` stat line next to
   `appliedTotal`. Use it instead of hand-computing; it is ESPN's own arithmetic, per category.
18. **Grep `fantasy/transcripts/` before ever saying a Lloyd read is missing.** The raw
   transcripts are on disk — 1.8MB, 22 team previews, recovered 23 Oct 2026 from the
   session log where they had sat unsaved since September. The `~/Desktop/lloyd_*.md` files
   are **summaries written 30 Sep from these**, and the source was then thrown away. On
   22-23 Oct I twice told the user "no Lloyd preview exists for Minnesota or Washington"
   and treated it as unfixable, while answering an Anthony-Davis-for-LaMelo trade. Both
   previews existed. Never present a summary's silence as the absence of evidence.
   **And when the user pastes source material, write it to disk in that same turn.**
19. **Verify before you claim — the tools exist, use them.**
   - Quoting Lloyd? `python3 fantasy/verify.py quote "<the words>"`. Zero hits means **do not
     attribute it**, no matter how certain it feels. Searching a player? `./fantasy/lloyd.sh
     <name>` — never a bare grep, because **21 of the league's biggest names return zero hits
     on their real surname** (Wembanyama, Doncic, Giannis, Haliburton, Edey, Maxey, Shai…).
     The captioner writes "Bazales" for Buzelis and "Edy" for Edey. **A silent zero-hit search
     looks identical to "he never said anything" — that is exactly how I invented a LaVine
     quote on 23 Oct and acted on it for two days.**
   - Reporting a score or a slate? `python3 fantasy/verify.py` (needs the env sourced).
   - A framework (LangChain etc.) does not help here and the user asked: every failure this
     session was a *verification* failure, not an orchestration one. Checks at the point of
     claim are the fix.
   ⚠ **`verify.py quote` PROVES THE WORDS EXIST. IT SAYS NOTHING ABOUT WHO THEY ARE ABOUT.
   5 Nov 2026.** I told the user Lloyd was leaning sell on Anthony Davis, quoting *"didn't
   have this guy on the sell high show, but I probably should have."* The string greps clean
   — **and it is about Kyshawn George.** Lloyd uses it as a *teaser* immediately before
   naming the next player: *"…24th ranked player over the course of the season. Well, didn't
   have this guy on the sell high show, but I probably should have. **What about Keshan
   George?** 25 points, seven assists, 71% shooting."* The user caught it: *"it was a p
   sudden transition but he was talking abaout kyshawn."*
   `split_players.py` could not save me here either — it cut the note to end on *"…What
   about"*, so the orphan teaser rode along **inside Davis's note**, because name-boundary
   cutting cannot catch a sentence that refers to a player it has not named yet.
   **So: a clean `verify.py` hit licenses the WORDS, never the SUBJECT. Before attributing
   any quote, read the sentences on BOTH sides of it and confirm the player is named in the
   same breath — and treat a note that ends mid-sentence or on "what about" as a boundary
   failure, not as content.** Lloyd's real AD read was the opposite: *"AD has been pretty
   good to start this season… the blocks have been a little bit down for AD. So that's good
   to see."*
20. **Read `totalPointsLive`, never `totalPoints`.** ESPN's `totalPoints` on a matchup
   **lags by a day** — it excludes the current scoring period entirely. `totalPointsLive`
   is the real score, and `winner` ("UNDECIDED" vs a team id) is the only reliable signal
   that a matchup has closed. On 25 Oct 2026 I reported the week as a 1134-995 win by 139;
   the true live score was **1278-1273, a 5-point lead, still undecided.** I repeated the
   wrong number three times before the user forced a re-check.
   **Also never report an in-progress slate as final.** Check every game's status first; a
   player at 18 minutes in the third quarter is not a result. I filed Edey at 28 when he
   finished at 43, and called a night a 100-point shortfall off partial box scores.
   **And normalise team abbreviations** — the fantasy API says WAS/SAS/NOP/GSW/UTA/NYK, the
   public scoreboard says WSH/SA/NO/GS/UTAH/NY. Mismatches silently drop players from
   "who plays today."
   **This applies to AVERAGES too, not just matchup scores.** ESPN season-total stat lines
   (`statSourceId: 0`, `statSplitTypeId: 0`) **absorb in-progress games**, so during a live
   slate `players.per_game` understates everyone currently playing. On 31 Oct 2026 Wembanyama
   read 60.3/g against a 65.4 completed-games average, Coward 34.6 vs 39.0, LaVine 34.0 vs
   39.8, Amen Thompson 37.0 vs 43.2, Edey 22.6 vs 28.8 — and Brandon Miller was the reverse
   (39.7 vs 38.0) because his game had already gone final. Quote completed-games numbers out
   of `game_grades` whenever a game is running.
   **And it corrupts the USAGE axis too — the third face.** `grade.py` scales projected
   volume into a USG%% with `k = 100*(team minutes/5)/team shot equivalents`, and each
   player's `k_mean` pools **all** his games. A game still in progress has partial team
   totals, so its denominator is small and `k` comes out enormous, inflating that player's
   `usg_proj` and deflating every usage ratio he has. Measured 1 Nov 2026 against the same
   players once final: Amen Thompson 0.64 `FROZEN` -> **0.985**, Wembanyama 0.82 -> 1.083,
   Coward 0.65 -> 0.837, Edey 0.55 -> 0.741. I had reported Amen's 0.64 to the user as a
   real role collapse and made it the top watchlist item. `team_context()` now skips games
   that are not `status.type.completed` — but **never trust a FED/FROZEN label taken
   mid-slate**, and run `grade.py --final` only once `verify.py slate` says all games are final.
21. **Judge a trade only by its effect on MY roster.** What the other team needs, what
   they are short of, whether they are "desperate," and whether I could extract more
   elsewhere are all irrelevant to whether a given 1-for-1 helps me. The only inputs are:
   points into my starting ten, slot and position coverage, and injury risk to my own
   lineup. User called this out 23 Oct 2026 — I had padded the AD/LaMelo answer with
   "Top G needs a big" and an unasked-for note about Paul George. Both noise. See rule 11.
22. **Audit the minutes inside any projection before quoting a value built on it.** Print
   projected mpg next to last season's actual mpg and this season's to date. ESPN's
   projections routinely assume a minutes *jump* that the rotation is not delivering, and
   minutes are the largest term in the valuation — so the error flows straight through.
   Caught twice on 23 Oct 2026: Buzelis projected 31 mpg on a Chicago team where **nobody
   plays above 32 per 48** (re-priced 35.1 → 26-30/g), and LaMelo projected *up* to
   32.9 mpg after 28.0 last season and 26.0 actual (which moved AD's trade break-even from
   49 games to 29). Also normalise raw minutes to **share of team minutes** before calling
   anything a benching — team pace and rotation depth set the scale.

23. **Any question about a player starts with `./fantasy/p.sh <name>`, then outside
   analysts, unasked.** Two standing instructions, both from the user.
   **(a) 2 Nov 2026: "when i ask u abt a player you should get general idea or trend about
   players via our small db. so use it please dont keep reading from the notes."** So step
   one is **always** `./fantasy/p.sh <name>` — one local call, ~0.03s, no API round-trip,
   which prints WHO / LEVEL / AXES / TREND / SPLIT / LLOYD / OURS. It resolves nicknames
   and caption manglings (`wemby`, `edey`, `cmb`, `bales`), marks the matched alias inline
   with `>>...<<`, and ranks Lloyd hits by **bm25 relevance** as short snippets instead of
   700-character blobs. Steer it with `--q "<terms>"` when the question is specific
   ("turnovers", "minutes", "shoulder") and widen with `--lloyd N`.
   **Do not read `fantasy/lloyd-daily-notes.md` to answer a player question** — the notes
   are a paraphrase of what `p.sh` reads straight from the DB, and a paraphrase is how
   rule 14 happens. Notes are for *writing* to, not for retrieving from. Only drop to
   `./fantasy/lloyd.sh <name>` for the full passage once a snippet looks load-bearing,
   and to `q.sh` to read a `research.finding` in full.
   **(b) 26 Oct 2026: "implicitly yiu should do this whenever i ask u abt a player."** So
   after `p.sh`, always **a web search for what other analysts are saying**, dated and
   attributed. Do not wait to be asked.
   **Measured 2 Nov 2026, 20 timed runs each:** one player question **0.355s → 0.024s
   (15x)**, 5 shell calls → **1**, 1 ESPN API call → **0**, 1.61 MB of JSON parsed → **0**.
   ⚠ Be precise about *where* that came from: the old **local** queries were already only
   0.021s. Essentially the entire gain is deleting the **0.334s** ESPN round-trip. The SQL
   was never slow and `p.sh` did not make it faster.
   On Lloyd retrieval, over a **127-case** gold set across 45 players: old date-ordered
   `lloyd.sh` (4 passages) scored **48/127 (38%) on 326,295 chars**; `p.sh` scores
   **68/127 (54%) on 97,980** — **+16pp recall on 70% less text**, and 6,798 → 1,441 chars
   per answer found.
   ⚠⚠ **THE FIRST VERSION OF THIS BENCHMARK WAS n=8 AND IT LIED.** On 8 hand-picked cases,
   windowing looked like it cost recall (4/8 vs 5/8), so I ripped it out and shipped full
   passages — then wrote "the win came from ranking, not trimming" into this rule as a
   lesson. At n=127 recall is **identical (54%) at every window width from 380 to 550 to
   full passage**, so the n=8 result was noise and I had removed a free 2-3x saving on the
   strength of it. **Eight cases cannot separate two configs.** The 127-case set is
   generated, not hand-picked: passages containing exactly one rostered player's alias
   (unambiguous attribution), an answer phrase unique in the corpus, and query terms taken
   from the passage but *not* from the answer, so it is not circular.
   **2 Nov 2026 — per-player segmentation added, and it is a QUOTE-SAFETY fix, not a
   recall fix. Be exact about which.** User: *"make sure to organize it based on players
   and not cram it."* `fantasy/split_players.py` cuts each transcript at **player-name
   boundaries** instead of a blind 700-char mark, because Lloyd's recaps are strictly
   player-by-player, so the names ARE the topic boundaries. 961 attributed notes, mean
   561 chars, in `lloyd_player_notes` + `lpn_fts`. `p.sh` prints these FIRST, then the
   old windowed segments as `LLOYD-WIDE`.
   Measured on the same 127-case gold set and the same corpus:

   | Config | Recall | single-subject passages | other players per passage |
   |---|---|---|---|
   | OLD `lloyd.sh`, 4 full passages | 68/127 (53.5%) | 59.0% | 0.59 |
   | `p.sh` 2 segments, 380-char window | 68/127 (53.5%) | 76.7% | 0.27 |
   | **player notes** | **14/127 (11.0%)** | **96.4%** | **0.05** |

   ⚠ **Notes RECALL 11% vs 53.5% — they are a retrieval REGRESSION and must never replace
   the segment search.** They cover only ~25% of the corpus (tracked players only, ~561
   chars each), so most answers are unreachable through them. Adding them to the segment
   pass gained **zero** recall (still 68/127) at 2.5x the text. What they buy is the thing
   that has actually cost us: cross-player contamination falls from **23.3% of returned
   passages to 3.6%** — 5.4x fewer chances to misattribute a quote. **So: notes to READ
   and QUOTE from, segments to FIND with.** The rule-23 mislabel is now structurally fixed
   — "30 plus minutes" resolves to **Josh Giddey**, not Buzelis.
   Three things this got wrong first, all observed:
   **(1)** auto-adding any 5+ char surname collapsed Jamal/Keegan/**Dejounte** Murray into
   one player and Klay/Ausar/**Amen** Thompson into another — worse than the chunking it
   was curing. Curated aliases only now, `hits > 0`.
   **(2)** these transcripts carry `h:mm:ss` as well as `m:ss` stamps and `index_lloyd.py`
   only stripped `\d+:\d+`, so timestamp noise rode through.
   **(3)** chapter headings leaked into bodies, putting Lloyd's **heading** ("Murray-Boyles
   turns a corner") inside quotable text — an attribution risk, not a cosmetic one.
   **Rebuild order matters and is easy to get wrong:** `index_lloyd.py` →
   `aliases.py` → `split_players.py`. Aliases score `hits` against the FTS index, so
   segmenting before reindexing silently drops every new mangling (it dropped Amen).
   The script prints any tracked player with no occurring alias — that warning is how
   `Giddy`, `Zakiti`, `Mari Boils`, `Weby`, `Yani Ant Kmpo` and `a man Thompson` were
   found, and how it surfaced that **Paul Reed, Paul George and Jeremiah Fears were never
   in `aliases.py` at all** — three of my own players for whom every search had been
   silently returning nothing. 161 → 215 aliases.
   Also validate a gold label *twice* — mine initially tested "Buzelis + 30 plus minutes",
   and that phrase is Lloyd talking about **Giddey**, with Buzelis entering as "the other
   guy." A snippet is a WINDOW, not a sentence: read the full passage before quoting.
   ⚠ `--q` is not optional politeness — it is how you find things. On 2 Nov,
   `./fantasy/p.sh garland --q turnovers` surfaced, in a transcript already on disk, that
   Lloyd had both **confirmed the turnover mechanism** ("his turnovers are are huge...
   averaging before today five turnovers a game") and reported that Garland **"banged up
   his shoulder"** on 1 Nov — while ESPN still read `ACTIVE`. I had told the user minutes
   earlier that no current injury reporting existed. An unsteered search had not found it.
   **Check the publication date on everything** — a July or last-season piece reads as
   current in search results and three of the first six hits on Wembanyama's slow start
   were from 2024 or preseason. Roster the analysts in
   `fantasy/analysts.md` and record findings in the `research` table.
24. **Not all "points league" rankings describe THIS points league.** ESPN default pays
   **STL +4 and BLK +4** — the highest of any mainstream points format. Yahoo-style
   points leagues pay 2 and often less, which is why RotoWire can write that in points
   leagues "the blocks that make him a category-league cheat code are worth less here."
   That is true of their format and **false of ours.** A ranking built on generic points
   scoring systematically **undervalues shot-blockers and steal men** for us, and our
   DD/TD/OREB/GP/TW bonuses are in nobody's list. Always say which scoring a borrowed
   rank was built in. Best practice: we already
   compute real applied points for all 126 rostered players in our exact scoring, so
   **use analysts for mechanism — role, minutes, usage, injury — and never for ranks.**
25. **Do not cite ESPN's fantasy analysts.** User, 26 Oct 2026: "no dont follow espn
   rankings. i dont like there analysts at all so lets find someone else." That rules out
   Snellings, Moody, Karabell, McCormick, Alexander and Florio, including ESPN's H2H
   Points rankings and points draft tiers. ESPN's **API and projections** are still the
   data source — this is about their written analysis and ranks. The replacement bench is
   `fantasy/analysts.md`: Josh Lloyd first, then Raphielle Johnson and Noah Rubin
   (Rotoworld) for per-player mechanism, Dan Titus (Yahoo/NBA.com) and Jacob Dunne
   (FantraxHQ) for points-specific reads.

26. **Source weighting — resolution order.** User, 26 Oct 2026: "if lloyd explcitiy says
   something follow that. if its left vague use these analysts and rank em based on the
   best or more accurate in general." So: **(0)** hard data from `league.db` always first —
   opinion sets direction, data sets size; **(1) Lloyd explicit** — a verbatim dated quote
   that greps clean and is *on the actual question* — follow it; **(2) Lloyd implicit** —
   he addressed the situation but not the question, use as a strong prior and say it is
   inference; **(3) weighted analyst consensus** — full table in `fantasy/analysts.md`,
   led by Raphielle Johnson and Noah Rubin (Rotoworld) because both have given a
   *mechanism* our own numbers later confirmed; **(4) my own calc, labelled as mine.**
   Lloyd does **not** get tier 1 on our bonus scoring (he does not know our settings), on
   anything he has retracted, or on a single-game reaction. Distinguish "explicit about
   draft value" from "explicit about tonight" — they are different questions.

27. **Grade every game against the player's OWN expected level, and keep minutes, rate
   and usage separate.** `python3 fantasy/grade.py` (needs the env) rebuilds `game_grades` and
   `player_form` for every rostered player in the league. Baseline is the player's own
   projected points-per-minute times the minutes they actually played — because 30 fpts is
   an ELITE night for Murray-Boyles and an AWFUL one for Giannis, so a league-wide grade is
   useless for buy-low / sell-high. Grades are ELITE / GOOD / NORMAL / POOR / AWFUL at
   ±0.5 and ±1.5 SD, and the SD is **measured** from the league's own games
   (2.175 on resid/sqrt(expected) over 308 games), not assumed. Alongside it a **minutes**
   grade (ROLE-UP / MINS+ / MINS-OK / MINS-DOWN / BENCHED) as a ratio of projected mpg,
   and a **usage** grade (FED / USG+ / USG-OK / USG-DOWN / FROZEN) as a ratio of the
   player's own projected USG%. **All three must stay separate** — and the reason is *who
   controls each one*, because that is what decides whether it reverts:

   | Axis | Measures | Controlled by | Reverts on its own? |
   |---|---|---|---|
   | **Rate** | pts/min vs own projection | the player | **yes** — the only one that does |
   | **Minutes** | mpg vs projected mpg | the coach | no |
   | **Usage** | USG% vs own projected USG% | the coach | no |
   | **Injury** | ESPN `injuryStatus` | nobody | **no — and it invalidates the other three** |

   **Injury is not a fourth axis, it is the confounder.** A hurt player shows rate down
   with minutes and touches intact — *precisely* the BUY LOW signature — but the rate will
   not regress while he is hurt, so the signal reads backwards exactly when it costs most.
   `player_form.injury` carries the flag and appends a warning to `note`. **Its blind spot
   is the dangerous part: it only knows what ESPN has published.** On 26 Oct 2026 Anthony
   Davis read `ACTIVE` while his own coach was telling reporters "I think he got hit in
   the hand" and the medical staff were evaluating him. **A clean `ACTIVE` is not evidence
   of health** — check the beat before trusting a BUY LOW on anyone with injury history.
   **Usage is the axis that breaks ties when minutes look fine.** User asked for it,
   26 Oct 2026: "i think u should factor usage as well... usage is a stat as well."
   ESPN publishes no usage rate but carries the inputs on *both* the actual and the
   projected (`statSourceId: 1`) stat line, so `FGA + 0.44*FTA + TOV` is recoverable;
   the team denominator comes from the **public box score** (`summary?event=<id>`,
   one call per game, 52 to backfill a week) giving a real
   `USG% = 100*(player_SE * teamMIN/5)/(MIN * team_SE)`. **Read it against 20.0%, which
   is league average by definition.** Two known limits, measured 26 Oct 2026 against a
   published USG% column: the fantasy API **rounds minutes to whole numbers** (Davis
   played 35:31, reported as 36, which alone moved him 30.4 -> 30.0), and the published
   column cannot be reproduced from box-score totals at all — solving backwards needs a
   team denominator of 103.2 for Davis but 98.2 for Sarr, so public columns are built on
   **on-court possessions**. Ours lands within ~1.4 points. Do not claim an exact match.
   What the axis buys:
   a player **missing shots he is still being given** regresses (true BUY LOW); a player
   who has quietly **stopped being given them** does not (`FADE (usage)`). Those two look
   *identical* on rate and minutes alone. It also demotes a rate spike that rides inflated
   touches to `SELL HIGH (usage)`, and surfaces `BUY (usage up)` when touches climb ahead
   of the box score. Caught on 26 Oct: Paul George's +1.02 rate was on 1.182 usage (not
   skill), AD's collapse was 1.169 usage at 44.0% FG (efficiency, not role — so a real
   buy-low), Coward's only broken axis was usage at 0.600 and climbing, and Buzelis was
   being *fed* at 1.35-1.40 while underperforming.
   **⚠ The baseline was BIASED HARSH and the user caught it, 29 Oct 2026.** Grading every
   game against ESPN's *projected* points-per-minute produced mean z of **−0.167** over 483
   completed games with **58.0% of all games below expected** — unbiased would be 0.000 and
   ~50%. Every label sat about a sixth of an SD toward the harsh end. For a player whose
   projection is stale it was far worse: ESPN had Anthony Davis at **1.742 fpts/min** while
   he was producing **1.240**, so a 43-point night on 34 minutes printed **POOR** when it was
   *above* his own season average. User's words: *"anthony davis had 43 fantasy points a
   couple below his general average but not crazy"* and on Reed, *"bad sure but hes just
   poor."* **Both were right; the regrade moved AD's night to NORMAL and Reed's to POOR.**

   **The fix is two baselines, because there are two different questions.**

   | Column | Baseline | Answers |
   |---|---|---|
   | `game_grades.z` / `grade` | **blend** of projection and the player's own demonstrated rate, shrunk with `K_PRIOR = 3` games | *Was this a good night **for him, as he is now**?* |
   | `player_form.form_z` → the **signal** | **pure projection** | *Is he below his **talent**?* — which is what BUY LOW / SELL HIGH mean |

   Keeping only the blend would have been wrong in the other direction: a blended z trends
   to zero by construction, so a season-long slump becomes invisible and **every signal
   collapses to HOLD** (it did — AD lost his BUY LOW until the split was added). Distribution
   after the fix: ELITE 6.0 / GOOD 20.5 / NORMAL 40.6 / POOR 25.5 / AWFUL 7.5, against an
   ideal 6.7 / 24.2 / 38.3 / 24.2 / 6.7.
   **Residual bias is −0.088, not 0** — about half the original. The rest looks like genuine
   league-wide underperformance against preseason projections, not a method error.

   **⚠ A MID-SEASON PICKUP HAS ALMOST NO GRADED GAMES, AND I QUOTED ONE AS A LEVEL.
   3 Nov 2026.** `grade.py` only grades games played **while the player sits on a roster in
   this league**, so a fresh pickup's `player_form` can rest on a single game while his
   season average covers seven. Fears was added 2 Nov; `game_grades` held **one** game — his
   5-of-17 worst — and I reported `rate z −1.65`, `usage 22.6%`, `SIGNAL BUY LOW` and "below
   replacement" as if they described him. `p.sh` printed `TREND 1 graded: 19` and I read
   straight past it. User: *"you are basing it on the bad one which is completely
   incorrect... be logical."* He was right.
   Real shape from the public game log: minutes **21/24/23/24/29/31/38** (monotonic) and
   fpts **6/8/15/17/81/44/16** — first four 11.5/g on 23.0 mpg at 0.500 fpts/min, last three
   **47.0/g on 32.7 mpg at 1.439**, ~3x per minute. **The 28.3 season average blends two
   roles and describes neither.** `p.sh` now prints `[n=N graded]` beside the rate and
   **refuses the axes** when `N < 3` or `N < 0.6 × GP` — rule 12 enforced in code.
   **Fix still owed:** `grade.py` should backfill games from before a player was rostered.
   Until then use the public log
   (`site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/<id>/gamelog`),
   and **get the id from `mRoster`, never by guessing** — I guessed one for Coward and pulled
   a different player's season. It also **includes preseason**: count only games from 20 Oct,
   which is why Fears shows 11 logged and `gp=7` is correct rather than a bug.

   **⚠ THE RATE AXIS PRODUCES A FALSE `BUY LOW` FOR ANY PLAYER WHOSE MINUTES HAVE
   EXPANDED. 4 Nov 2026 — this is rule 22 running backwards and it is structural.**
   `expected = projected points-per-minute × minutes actually played`, so a player promoted
   out of a bench role is measured against a **bench per-minute rate he was never going to
   hold at starter volume**. Paul Reed: ESPN projected 13.8 mpg at 1.796 fpts/min, he is
   starting 27.4 mpg because Jalen Duren is out, `min_ratio` **2.13** — and `p.sh` printed
   `SIGNAL BUY LOW`, `rate z -1.09`, grade **AWFUL**, while he was running **+12.6/g OVER
   his adjusted projection** (34.5 vs 21.9). Per-minute 1.796 → 1.354 is the *expected*
   shape of a role expansion, not a decline. **So: before believing a BUY LOW or a POOR,
   read `min_ratio` on the same line. Above ~1.4 or below ~0.7 the rate axis is comparing
   two different jobs and the label is void.** The real risk for such a player is the
   starter's return, not his rate — Lloyd had it right in one clause: *"obviously Jaylen
   Duran being out means he's able to do this."*

   **`game_grades.fpts` is ESPN's own `appliedTotal`** — authoritative, formula-free, and
   it supersedes `game-log.csv`'s hand-computed `fpts`. ⚠ **CORRECTED 2 Nov 2026: this rule
   previously said "off by ±1 on seven lines" and that was wrong on both counts.** Re-ran the
   join (`game_log` x `game_grades` on player+date, 36 of 37 rows match a graded game):
   **10 of 36 rows disagree (28%)**, and the errors are **not** all ±1 — they run from
   **−2 (Davis, 24 Oct) to +4 (Reed, 25 Oct)**, with LaVine +2 on 25 Oct. Seven of the ten
   are the ±1 cluster on 21 Oct. Never quote a number from this file without re-running the
   check that produced it. Rebuilt 26 Oct 2026 at the user's request.

28. **ESPN's projections run HIGH in this league — use `players.proj_adj`, not
   `proj_full`.** ⚠ **The magnitude SHRINKS as the season goes on — re-measure, do not
   quote this rule's headline.** On 31 Oct over 104 players with ≥5 GP it was **9.5%**
   (mean −3.95/g, 77 of 104 below). Re-run on 2 Nov over **107** players with 13 periods
   of data: mean −2.50/g, **68 of 107 (64%)** below, against a mean projection of 40.2/g
   = **6.2%**. Same direction, two-thirds the size, because players regress toward
   projection as games accumulate. A fresh temporal holdout run on 2 Nov (fit on periods
   1–9, 496 games; test on periods 10–13, 172 games, zero overlap) gives **k = 0.939**,
   cutting out-of-sample MAE **12.094 → 11.681 (+3.4%)** and mean signed error
   **−2.19 → +0.20**. The stored `proj_adj` still uses k = 0.905 from the 31 Oct fit. The miss splits
   almost exactly in half, and the halves mean opposite things:

   | Source | Effect | Controlled by | Reverts? |
   |---|---|---|---|
   | Minutes shortfall (mean −1.42 mpg, 76 of 104 below) | −1.88/g (47.5%) | the coach | **no** |
   | Rate shortfall | −2.07/g (52.5%) | the player | **yes** |

   Fitted a single multiplier on scoring periods 1–9 and tested on 10–11: **k = 0.905**,
   MAE 13.924 → 13.546, **+2.7% out of sample**. Refit on everything gives 0.907, and every
   individual period lands in 0.855–0.995 — never above 1.0. Stored as `players.proj_adj`
   (`delta_adj` is actual minus that). Mean error goes **−3.95 → −0.10**, beat/miss **25/104
   → 51/104**. This also closes rule 27's open question: the residual −0.088 grading bias
   is **real league-wide underperformance against preseason projections**, now quantified.
   ⚠ **Per-player corrections FAIL — do not rebuild them.** Adjusting each player from his
   own prior games is worse than leaving ESPN alone at every shrinkage tested (rate-only
   −2.5%, K=3/3 −1.9%, K=5/2 −0.5%, pure actuals −18.7%). Single-game fpts carry MAE ~12.7
   against a ~40 mean, so a 5-game sample adds more variance than the bias it removes. Only
   the league-wide constant survives, because it costs no variance.

29. **Refresh data with `refresh_players.py`; `build_db.py` is the heavy, risky path.**
   `. ~/.espn-fantasy.env && python3 fantasy/refresh_players.py` is self-contained, UPSERTs
   `players` in place for every rostered player, and reproduces rule 8's valuation exactly
   (validated 31 Oct: 115 of 116 stored `proj_full` values reproduced, mean |diff| 0.009).
   Then `python3 fantasy/grade.py` for grades and form.
   ⚠ **`build_db.py` emptied five tables on 31 Oct 2026.** It read `players` from a session
   scratchpad JSON that **no script in the repo produced**, and it DROPped
   players/lloyd_quotes/game_log/transactions/research *before* reading that input — so the
   documented rebuild wiped all five and crashed. `load_research.py` separately held only
   **29 of 136** research rows, so the documented `build_db.py && load_research.py` pair
   would have silently destroyed 107 findings. Both are now fixed (pre-flight input checks
   before any DROP; `players` and `research` are no longer dropped), but **back up
   `fantasy/league.db` before any rebuild** and only run `build_db.py` when you actually need
   `lloyd_quotes`, `game_log` or `transactions` rebuilt from disk.

30. **Report in FANTASY POINTS, not in z-scores, and do not reason from points-per-minute.**
   User, 5 Nov 2026: *"whenever u record ststs dont tell me those z numbers thosae are just
   for you to look at. just give m the fantasy numbers and dont look at per minute fantasy
   points its rlly just wrong and inconsistent. u look at just the overall stats, baskwtball
   is not as perfectly mathematical as u think."*
   **What this means in practice:**
   - **Never put `z`, `form_z`, `scaled`, SD units or `min_ratio`/`usg_ratio` decimals in a
     user-facing answer.** They stay internal — keep computing them, keep logging them in
     `research` and `player_form`, but translate before speaking. "Below his own level" not
     "z −0.63". "Touches climbing" not "usage ratio 1.31".
   - **Lead with the numbers he actually plays with:** fantasy points per game, the game log
     (e.g. 68 / 16 / 30 / 50 / 43 / 52 / 55 / 65), minutes, games played, totals, and the
     raw box categories — points, rebounds, assists, steals, blocks, turnovers, FG/FT.
   - **Do not build an argument on points-per-minute.** Use minutes and totals instead. If a
     role changed, say "he went from 20 minutes to 32 and scored X" — not "his rate fell
     from 1.796 to 1.354".
   ⚠ **He is right on the evidence, and our own files prove it.** Rule 27's own worked
   example is a per-minute failure: Paul Reed printed `BUY LOW` and a grade of **AWFUL**
   while running **+12.6 fantasy points per game over expectation**, purely because a bench
   per-minute rate was projected onto starter minutes. Rule 22 is the same error in the
   other direction. Per-minute rates are the single most error-prone number in this repo —
   they have produced more wrong calls than any other quantity, and he has now flagged them
   unprompted. **Minutes and role are the real variables; per-minute is a fragile derived
   quantity, not a fact about the player.**
   The three-axis grader stays as a *screen* — it is still how we spot a player whose
   touches moved before the box score did. But the screen is a pointer to go look, never
   the finding itself, and the finding gets reported in points.

31. **A BAD SHOOTING NIGHT AND A MINUTES LOSS ARE NOT THE SAME EVENT. Triage every poor
   line through minutes FIRST, and throw the shooting away.**
   User, 7 Nov 2026: *"there is a huge difference between bad shooting night and role loss
   or minute loss. If its a minutes reductin thats bad or a real concern due to a blowout
   is fine. if its a bad shooting night we can ignore it."*
   **The decision tree, in this order:**

   | What moved | Blowout explains it? | Verdict |
   |---|---|---|
   | **He left the game** | irrelevant | **INJURY — triage stops here.** Not a minutes read at all |
   | **Minutes down** | no | **REAL CONCERN** — the only thing on this table worth a watchlist item |
   | **Minutes down** | yes | **FINE** — say so and move on; it is the scoreboard, not the coach |
   | **Minutes fine or up, shooting bad** | n/a | **IGNORE** — do not report it as a bad night |

   ⚠ **THE INJURY ROW WAS MISSING AND IT COST ME ONE — user, 8 Nov 2026: *"brandon miller
   also got injured too like he left hte game early rememeber, but no status about future
   games was uopdated."*** On 6 Nov I filed Miller's **14 minutes** in a 39-point loss under
   *"minutes down, blowout did it → FINE."* **The blowout had nothing to do with it — he
   left the game.** Charlotte's coach: he *"started limping, and he asked for a sub after a
   couple of plays,"* was **ruled out** after heading to the locker room, and Tidjane Salaun
   started the second half in his place. An injury exit is neither "fine" nor "ignore": it
   is rule 27's confounder, which **invalidates all three axes**, and it is the one way a
   minutes drop carries forward to the next game. **So ask "did he finish the game?" BEFORE
   reaching for the margin** — a blowout and an exit produce the same low minutes number and
   mean opposite things.

   So **check the game margin before calling any minutes figure a benching**, and once
   minutes are cleared, a 3-for-11 is not a finding. Rule 12 already bans a one-game read;
   this says which *half* of a bad game is even eligible to be read.
   ⚠ **Caught applying this backwards on 6 Nov 2026.** I told the user Dejounte Murray's
   line was "the one genuinely bad line" of the night — 7 points on 3-11 for 18 fantasy
   points. **His minutes were 35 and they were UP on his own average.** It was a pure
   shooting night and belonged in the bin. Meanwhile I waved through **Ryan Rollins at 14
   minutes in a 14-point loss** — not a blowout, minutes trending 24 / 34 / 25 / 32 / 17 /
   26 / 17 / **14**, only 3 shot attempts — which is the one line on the slate that
   actually survives this rule. **I had the two exactly inverted**, because the grader's
   rate axis flags the shooter and says nothing about the bench.
   This is also *why* rule 30 bans per-minute reasoning: points-per-minute **mixes the two
   together**, so it is structurally incapable of telling a missed shot from a lost role.
   Note the asymmetry the user is pointing at: **shooting reverts and minutes do not** —
   the same split rule 27's table already makes between the player-controlled axis and the
   coach-controlled one. Report a shooting slump as noise; escalate a minutes cut.

## Files

| Path | What it is |
|---|---|
| `fantasy/game-log.csv` | Per-player game lines with fantasy points |
| `fantasy/matchup-log.csv` | Weekly matchup results |
| `fantasy/lloyd-daily-notes.md` | Lloyd's recap opinions, with caveats |
| `fantasy/watchlist.md` | Open questions with a dated trigger — check this each session |
| `fantasy/league.db` | **SQLite — the store. Query it first.** `players` (all 126 rostered, value + rates + Δ), `lloyd_quotes` (287, scored, verbatim), `game_log`, `transactions` (1173, incl. trade contents), `research` (my findings). Helper: `./fantasy/q.sh "SELECT ..."`. Rebuild: `python3 fantasy/build_db.py && python3 fantasy/load_research.py` |
| `fantasy/player-dossier.md` | Rendered view of the DB. The DB is the source of truth |
| `fantasy/transactions-log.{csv,md}` | Full league transaction history |
| `./fantasy/p.sh <name>` | **START HERE for any player question.** One local call: WHO / LEVEL / AXES / TREND / SPLIT / LLOYD / OURS. Resolves nicknames, bm25-ranks Lloyd snippets, `--q` to steer, `--lloyd N` to widen |
| `fantasy/split_players.py` → `lloyd_player_notes` | **One segment per PLAYER, cut at name boundaries — 961 notes, mean 561 chars.** What `p.sh` prints first. 96.4% single-subject vs 76.7% for windows. Quote from these; FIND with the segments. Rebuild AFTER `index_lloyd.py` and `aliases.py` |
| `./fantasy/lloyd.sh "<player>"` | **Full passages**, newest first — the drill-down once a `p.sh` snippet matters. FTS over all 2,995 passages / 349k words; auto-expands caption manglings via `name_aliases` |
| `fantasy/build_stats.py` → `stat_lines`, `stat_items` | **Cached ESPN stat lines for all 130 rostered players, both seasons, actual + projected.** This is what makes `SPLIT` a DB read instead of an API call. Rebuild after a roster change |
| `python3 fantasy/verify.py` | **Pre-claim checks.** `quote "..."` proves a quote is real; `score` gives the LIVE matchup score and whether it closed; `slate` says if games are still running |
| `fantasy/refresh_players.py` | **Refresh `players` in place from the API** — averages, projections, rule-8 bonus. Self-contained; UPSERTs, never drops |
| `fantasy/grade.py` → `game_grades`, `player_form` | **Per-game ELITE/GOOD/NORMAL/POOR/AWFUL vs the player's own level, on three separate axes — rate, minutes, usage — plus a SELL HIGH / BUY LOW / FADE / HOLD / AVOID signal.** Uses ESPN `appliedTotal` |
| `fantasy/analysts.md` | **Who to read and who not to.** Tiers, the STL/BLK calibration trap, ESPN exclusion |
| `fantasy/transcripts/` | **Raw Lloyd transcripts — grep HERE first.** 1.8MB, 22 team previews |
| `~/Desktop/lloyd_team_preview_notes.md` | Summaries of 22 teams, written 30 Sep. Lossy and stale |
| `~/Desktop/lloyd_positional_tiers.md` | Tiers, variance bands, corrections |
| `BETTING.md` | The archived betting project. Not current work. |

## Standing weaknesses to watch

- ~~**Dejounte is the only PG-eligible player.** If he sits, the slot is forfeited.~~
  ⚠ **FALSE SINCE THE FEARS PICKUP — corrected 3 Nov 2026.** Pulled `eligibleSlots` off
  `mRoster`: **Jeremiah Fears is PG/SG**, same as Dejounte. There are now **two**
  PG-eligible players and the slot cannot be forfeited by one absence. Dejounte is also
  sitting on **IR**, so while he is out he costs no scoring slot at all. The user made
  this weakness obsolete by accident and it sat wrong in this file for days — re-derive
  eligibility from the API, never from memory. Full roster: only 6 of 15 are G-eligible
  (Fears, Dejounte, Amen, Miller, Coward, LaVine), so GUARD depth is the real constraint,
  not PG specifically.
  ⚠⚠ **AND IT WENT STALE AGAIN IN 48 HOURS — re-checked 5 Nov 2026.** **Fears was dropped**
  and **Ryan Rollins added** (ESPN `mTransactions2`, 07:51 on 5 Nov, with Paul Reed as the
  drop). The conclusion survives but **for a different player**: Rollins is **PG/SG**, so
  there are still two PG-eligible bodies (Dejounte, Rollins) and 6 of 14 are G-eligible
  (Dejounte, Rollins, Amen, Miller, Coward, LaVine). Dejounte is **not** on IR any more —
  he is ACTIVE and in the PG slot; Keegan Murray holds the only IR spot. **The lesson is
  not "this bullet was wrong," it is that a roster fact in a file is stale the moment the
  user makes a move, and the user moves between sessions.** Pull `mRoster` first, every
  time, before saying anything about slots, IR or eligibility.
- **Anthony Davis is the biggest single risk** — 20 games last season, and GP is +1.
  ⚠ **UPDATE 5 Nov 2026 — the user's read, and it has both a quote and the behaviour behind
  it.** AD stated publicly (Twitch / Fanatics Fest) that he wants to play **all 82**,
  answering "82" to "how many games played for you?", and adding that he does not care
  about his stats. **Through 8 team games he has played 8**, at **33.1 mpg vs 31.2 last
  season** — so he is playing *more* per night, not being managed — and he finished the
  4 Nov game on a wrapped ankle for 65 fpts (GOOD, z +1.42).
  ⚠⚠ **THAT "8 OF 8" IS STALE — RE-CHECKED 8 Nov 2026. He is now 8 of Washington's 10:
  he missed TWO games, and they were BOTH LEGS OF A ROAD BACK-TO-BACK** (@ATL 6 Nov,
  @OKC 7 Nov). He does not appear in either box score; ESPN logged period 19 as a 0.0 with
  him sitting in a starting slot. Still **Day-To-Day** with **no injury type published**.
  The wrapped ankle on 4 Nov is the obvious suspect but nothing is confirmed. So the
  all-82 quote is a stated intention rather than observed behaviour for now — but **two
  games off the back end of a back-to-back is the most ordinary absence pattern there is,
  and it is NOT yet evidence against the all-82 read.** Next opportunity: **Mon 9 Nov
  @ DET**, so no new information until then. The valuation below is unchanged.
  ⚠ **COUNT MISSED GAMES, NEVER "SCORING DAYS AT ZERO" — user correction, 8 Nov 2026.** I
  first wrote this up as "zero for three consecutive scoring days," counting 8 Nov, a day
  **Washington does not play.** User: *"AD only missed 2 days the whole back to back
  basically."* A day with no game scheduled is not an absence, and padding the count that
  way makes a routine two-game sit read like an escalating injury. This is the **same**
  no-game-day error as the 7 Nov bench-slot one (*"uh thats because they dont have a
  game?"*) — **check the team's schedule before turning any zero into a trend.** A zero on
  a no-game day is a MATCHUP fact (he cannot help week 3 any further) and never a
  DURABILITY fact; keep the two apart.
  Priced under rule 9: ~16.4/g
  over a ~31/g replacement means **every 10 extra games ≈ +164 points**, i.e. 20 GP → ~328
  for the season vs 65 GP → ~1,066. **That single question outweighs every lineup tweak and
  waiver add on this roster.** Counterweight, kept honest: his per-minute rate is −16.6% on
  last season, concentrated in **blocks (1.65 → 0.86) and OREB (3.10 → 1.43)** — the
  categories an availability-first big sheds, and the ones our bonuses pay most for. n=8, so
  do not commit to the mechanism; his last four games (53.8/g at 1.629/min) are *above* last
  season's per-minute. Either way the trade favours us: 45/g × 65 games beats 50/g × 20.
- Top-heavy: Wemby, Giannis and AD are ~40% of output, with a replacement-level bench.
