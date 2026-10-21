---
description: Log last night's games from ESPN and report what matters
---

Read ESPN Daily Leaders for the most recent slate
(`https://fantasy.espn.com/basketball/leaders?leagueId=1858125890`), with Scoring Type on
LeFantasy. Screenshot the table rather than relying on the accessibility tree — the point
values are not in it. Scroll the inner table sideways so blocks and turnovers come through
instead of being left blank.

Then:

1. Append every line to `fantasy/game-log.csv`. Blank means unread, never zero.
2. Update `fantasy/matchup-log.csv` with the current matchup score.
3. Report: my roster's performances with the stat line behind each score, then my
   opponent, then anything league-wide that changes a decision.

Skip waiver and free-agent names unless genuinely season-changing. Do not commit.
