# Season logs

Append-only records so trends can be tracked across the season. Claude writes to these
after reading ESPN; without them every session starts from zero.

| File | What it holds |
|---|---|
| `game-log.csv` | One row per player per game: full stat line plus fantasy points |
| `matchup-log.csv` | One row per weekly matchup |

**game-log.csv columns:** `date, player, pro_team, opp, result, min, fgm, fga, ftm, fta,
tpm, oreb, reb, ast, stl, blk, tov, pts, fpts, fantasy_team`

`fantasy_team` uses the ESPN abbreviation, `FA` for a free agent. Blank cells mean the
value was not readable on the page, not zero — ESPN's Daily Leaders table cuts off the
blocks and turnovers columns unless it is scrolled sideways.

## How to update

Ask Claude to **log last night's games**. It reads ESPN Daily Leaders, appends the rows,
and leaves the file uncommitted.

## What it is for

- per-player trends — is a player's role growing or shrinking
- minutes and usage changes over time
- how each player actually scores in this format, not how they look in a box score
- what each weekly matchup was won or lost on
