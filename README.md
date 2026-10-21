# NBA Fantasy Analyst

A Claude Code project that helps run a 9-team ESPN fantasy basketball team.

Claude reads expert podcast transcripts, keeps notes on every NBA team and player,
knows the exact scoring rules of this league, and connects to ESPN in Chrome to read
live data. It is used to rank players, plan drafts, judge trades, and compare rosters.

> **This project used to be about sports betting.** That work is finished and still
> lives here — see [BETTING.md](BETTING.md). The headline result was an **ROI of
> −4.77%**, meaning the model found no edge against the market. The project has since
> been repurposed for fantasy basketball, which is what this README covers.
>
> The betting pipeline may be revisited later using the season logs in `fantasy/` as an
> input — but not until there is enough of a sample to show real trends. See
> [Future: feeding the logs back into betting](#future-feeding-the-logs-back-into-betting).

---

## 1. The league

| | |
|---|---|
| **Name** | LeFantasy |
| **Platform** | ESPN Fantasy Basketball |
| **League ID** | 1858125890 |
| **My team** | The Freaky Alien Clubhouse (team ID 6) |
| **Teams** | 9 |
| **Format** | Points league (not categories) |
| **Draft** | Snake, 13 rounds, drafted from slot 3 |

### Scoring

This is **ESPN's default points scoring plus bonuses**. The first group is identical
to ESPN's defaults. The second group is what this league adds on top.

**Standard (same as ESPN default):**

| Stat | Points |
|---|---|
| Point scored | +1 |
| Field goal made | +2 |
| **Field goal attempted** | **−1** |
| Free throw made | +1 |
| **Free throw attempted** | **−1** |
| Three pointer made | +1 |
| Rebound | +1 |
| **Assist** | **+2** |
| **Steal** | **+4** |
| **Block** | **+4** |
| **Turnover** | **−2** |

**Added by this league:**

| Stat | Points |
|---|---|
| Game played | +1 |
| Offensive rebound | +1 (on top of the rebound) |
| Double-double | +3 |
| Triple-double | +5 |
| Quadruple-double | +25 |
| Team win | +1 |
| Ejection | −2 |
| Flagrant foul | −1 |

### What the scoring rewards

- **Steals and blocks are worth 4 each** — the most of any single event. One block is
  worth four rebounds. This is why rim-protecting bigs and ball-hawking wings are so
  valuable here.
- **Assists are worth double rebounds.** High-assist guards and point-forwards gain.
- **Missing shots costs you.** Every attempt is −1, so a player who takes 20 shots and
  makes 7 is actively losing points. High-volume, low-percentage scorers fall.
- **Free throws can be negative.** A made free throw is net 0 (+1 made, −1 attempt).
  A missed one is −1. High-volume poor free-throw shooters lose real points.
- **Double-doubles are worth 3 each.** Over a season a nightly double-double player
  earns roughly 200 extra points. This is the single biggest difference between this
  league and standard ESPN points, and it is easy to forget.
- **Games played is worth +1.** Durability is scored directly. A player who misses 20
  games loses more than just his production.

### Roster

10 starters, 3 bench, 2 IR slots.

`PG` · `SG` · `SF` · `PF` · `C` · `G` · `F` · `UTIL` · `UTIL` · `UTIL`

Only the 10 starters score. **Bench players contribute nothing** unless someone is
hurt — which matters a lot when deciding whether to trade two players for one.

### Transactions

| | |
|---|---|
| Adds per matchup | 3 |
| Adds per season | No limit |
| Trades | No limit |

---

## 2. The team

**The Freaky Alien Clubhouse** — drafted from slot 3 of 9, snake, 30 September 2026.

### Draft results

| Round | Pick | Player | Pos |
|---|---|---|---|
| 1 | 3 | Victor Wembanyama | C |
| 2 | 16 | Tyrese Haliburton | PG/SG |
| 3 | 21 | Amen Thompson | SF/SG |
| 4 | 34 | Lauri Markkanen | PF/SF |
| 5 | 39 | Anthony Davis | C/PF |
| 6 | 52 | Dejounte Murray | SG/PG |
| 7 | 57 | Brandon Miller | SF/SG |
| 8 | 70 | Paul George | SF/PF |
| 9 | 75 | Matas Buzelis | SF/PF |
| 10 | 88 | Keegan Murray | PF/SF |
| 11 | 93 | Cedric Coward | SF/SG |
| 12 | 106 | Zach Edey | C |
| 13 | 111 | Nic Claxton | C |

Picks in a 9-team snake from slot 3 land at 3, 16, 21, 34, 39, 52, 57, 70, 75, 88, 93,
106 and 111. The gaps alternate 13 then 5, so every odd round is a short turn.

### Trades

**1. Haliburton + Markkanen → Giannis Antetokounmpo** *(with Top G)*

Why it was made:

- Giannis is **4th in ESPN points** and his value is rising — Miami takes him from 29 to
  32-33 minutes with his assist rate up and 37% usage intact. He was already 10th in
  fantasy scoring on a part-time workload.
- Haliburton was the **widest-variance player on the roster** (best case 8th, worst case
  55th) and his season is front-loaded with rust: back-to-backs off, poor efficiency
  until roughly Christmas.
- Markkanen was the one genuine reach of the draft — taken at 34, ADP 71 — with a
  ceiling capped because three or four Jazz players will clear 20 points.
- It kept Amen and Anthony Davis, who are the second and third biggest steals-and-blocks
  sources on the roster.

Effect on the starting ten: **+12.1 projected fantasy points per slate.**

### Current roster

**Starters**

| Slot | Player | Team |
|---|---|---|
| PG | Dejounte Murray | NO |
| SG | Amen Thompson | HOU |
| SF | Cedric Coward | MEM |
| PF | Giannis Antetokounmpo | MIA |
| C | Victor Wembanyama | SA |
| G | Brandon Miller | CHA |
| F | Anthony Davis | WSH |
| UTIL | Paul George | BOS |
| UTIL | Matas Buzelis | CHI |
| UTIL | Keegan Murray | SAC |

**Bench:** Zach Edey (MEM), Zach LaVine (SAC), Collin Murray-Boyles (TOR)

### Known weaknesses

- **Only one point-guard-eligible player.** Dejounte is it. If he sits, the PG slot is
  forfeited, and a zero at a starting slot costs more than any bench player gains.
- **Top-heavy.** Wemby, Giannis and Anthony Davis are roughly 40% of the projected
  output. The bench is replacement level, so an absence at the top costs 25-35 points a
  game with nothing to absorb it.
- **Anthony Davis is the single biggest risk.** He is the second-largest block of
  production and carries the longest injury history on the roster.
- **Zach LaVine is a bad fit for this scoring** — the biggest loser in the format
  adjustment, because of the field-goal-attempt penalty.

---

## 3. What Claude has been trained on

"Trained on" here means: transcripts were pasted into Claude, and Claude wrote them up
into permanent notes files. Claude did not learn these as a model — it reads the notes
each session.

### Main source: Josh Lloyd (Locked On Fantasy Basketball)

The primary expert for this project. His opinions outrank ADP and outrank other
podcast hosts. Shows processed:

| Show | What it gives |
|---|---|
| **30 team previews** | Per-player reads for every NBA team, usually with a local beat reporter |
| **5 positional tier shows** | PG, SG, SF, PF and C tiers, with points-league tiers stated separately |
| **Top 25 show** | Full top-25 rankings given separately for **ESPN points**, **Yahoo points** and categories |
| **Variance show** | Best case and worst case (20th to 80th percentile) per player, by round |
| **Busts show** | Explicit anti-hype names to avoid |
| **Bounceback show** | Players expected to recover value |
| **Sleepers show** | Late-round and waiver targets |
| **Correlation show** | How teammates' values interact |
| **4 September team previews** | Updated Denver, Dallas, Cleveland and Atlanta reads |

One gap: **Lloyd never recorded a Miami preview** — he lost the audio to a Windows
update. The Heat notes come from his draft-night Giannis-trade reaction show, so
anything about Miami's supporting cast is out of date.

### Other sources

- **ESPN** — live rosters, projections and box scores, read through Chrome
- **CBS projections** — the per-game projection on the draft board (see the warning below)
- **RotoWire, RotoBaller, Fantrax, Mike Snellings (ESPN)** — secondary rankings, used
  for cross-checking only
- **Beat reporters** — quoted inside Lloyd's team previews

### Where the notes live

| File | Contents |
|---|---|
| `~/Desktop/lloyd_team_preview_notes.md` | All 30 teams, player by player, with a verdict and a target rank for each |
| `~/Desktop/lloyd_positional_tiers.md` | Positional tiers, the variance table, a corrections log, and a section on how Lloyd reasons |
| [Draft board artifact](https://claude.ai/artifact/XW6eYEmUEjPt5pzRRhkhVw) | 117 ranked players, a waiver list, and the 13-round draft plan |

---

## 4. How to run it

Everything runs through **Claude Code** in the terminal.

```bash
cd ~/Desktop/nba-fantasy-analyst-agent
claude
```

Then just talk to it. Examples:

```
what did lloyd say about jaren jackson
is trading amen and markkanen for giannis worth it
who should i start tonight
rank all nine teams in the league
```

### Feeding it new podcast episodes

Paste the transcript straight into the chat and say which team or show it is. Claude
will read it and add it to the notes files. Tell it to **update the notes**, otherwise
it only answers your question and the episode is lost when the session ends.

### Reading live ESPN data

Claude connects to **your actual Chrome browser** using the Claude in Chrome extension.
It opens a new tab, uses your existing ESPN login, and reads the page. It does not log
in as you and it does not change anything unless you ask it to.

To use it, open your league in Chrome and paste the URL:

```
https://fantasy.espn.com/basketball/team?leagueId=1858125890&teamId=6
```

Claude can then read live fantasy points, rosters, box scores, the waiver wire and
other teams' lineups.

### Memory

Claude keeps notes about this project between sessions in
`~/.claude/projects/-Users-shayan-Desktop-nba-fantasy-analyst-agent/memory/`.
Things like the scoring rules, which sources to trust, and mistakes not to repeat.

---

## 5. Rules Claude follows

These were learned the hard way during the draft. They are written down so the same
mistakes do not happen again.

**1. Use the points-league tier, not the category tier.**
Lloyd gives both. The category tier is the default and it is the wrong one for this
league. His 9-cat rankings badly under-rate Giannis (69th) and Banchero (133rd) and
over-rate Kessler, Clingan and Kel'el Ware.

**2. Convert his rounds to overall picks.**
Lloyd talks about 10-12 team leagues. This league has 9 teams. His "round 4" means
overall picks 37-48, which here is rounds 5-6. Always convert before comparing.

**3. Use his ESPN points ranks directly when he gives them.**
He ranks separately for ESPN points, Yahoo points and categories. The ESPN points list
is the one that matches this league's base scoring. Only adjust for the extras this
league adds — double-doubles, triple-doubles, offensive rebounds and games played.

**4. Do not use the draft board's FP column to compare teams.**
That number is a CBS projection in ESPN *default* scoring. It contains **no
double-double, triple-double, offensive rebound or games-played bonus at all.** Using
it to rank rosters badly over-rates double-double bigs and rookies. Ask for the real
ESPN projected points instead.

**5. Quote his most considered opinion, not his most flattering one.**
He thinks out loud and will float a name high before settling lower. Check what he says
when he is actually making the list, and check the player's points-league finish, before
treating a quote as a ranking.

**6. Rank on healthy per-game potential, then penalise for injury.**
His own method: per-game talent sets the tier, injury history moves the draft pick. Do
not rank a player low just because he missed games — and do not ignore it either.

**7. Bench players are worth zero.**
Only 10 of 13 roster spots score. Trading two players for one better player is usually
right in a 9-team league, because the empty spot gets filled from a deep waiver wire.

---

## 6. Repo layout

| Path | What it is |
|---|---|
| `README.md` | This file — the fantasy project |
| `fantasy/` | Season logs — every game line and every matchup result |
| `BETTING.md` | The old betting-market project, complete and still runnable |
| `R/` | R code for the betting pipeline |
| `data/`, `output/` | Data and results for the betting pipeline |
| `tests/` | Tests for the betting pipeline |
| `RUNBOOK.md` | In-season runbook for the betting pipeline |

The fantasy work has no code. It is notes files, a published draft board, the season
logs in `fantasy/`, and Claude Code reading them.

**Keeping the logs current matters.** Claude has no memory of a game it is not told to
write down. Ask it to **log last night's games** regularly, or the season's trends
cannot be reconstructed later.

---

## Future: feeding the logs back into betting

Not now — the game log needs months of data before it means anything. Noting the plan so
it is not lost.

`BETTING.md`'s pipeline already has the piece this would plug into: `R/10_player_projection.R`
builds a team's projected points from **per-player minutes times scoring rate**, which is
the same shape as `fantasy/game-log.csv`. That module exists because the betting model's
real problem was never accuracy — it was that every feature was team-level history, which
is exactly what a betting line is already made of. A forecast built from players up is a
genuinely different input.

One design rule to protect now, while the log is still being filled: **a row must only
ever be used to predict games that came after it.** The log records what already happened,
which is fine for spotting trends, but any model built on it has to use strictly prior
games or it is reading the answer. That is the rule the whole betting project was built
around and it is easy to break by accident.

---

## Licence

MIT — see [LICENSE](LICENSE). The licence covers the code in this repo. Podcast
transcripts, ESPN data and third-party projections belong to their owners and are used
here as private reference notes, not redistributed.

**Not betting or financial advice.** See [BETTING.md](BETTING.md) for the full result
of that work, which found no edge.
