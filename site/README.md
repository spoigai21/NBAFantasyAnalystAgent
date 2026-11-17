# Rankings site

Static, frontend-only. Four files, no framework, no build step, no API.

| File | What it is |
|---|---|
| `index.html` | The page |
| `styles.css` | Theme — tokens lifted from `eighthold.com/styles.css` so the two read as one system |
| `app.js` | Renders the table, the current / projected toggle, search and the my-team filter |
| `rankings.json` | The data. **Generated — never edit by hand** |

## Updating the data

```bash
. ~/.espn-fantasy.env \
  && python3 fantasy/refresh_players.py \
  && python3 fantasy/rankings.py \
  && python3 fantasy/build_site_data.py
```

`build_site_data.py` imports `rankings.py` and uses its `load()`, `MANUAL_PROJ` and `rank()`
directly, so the site can never disagree with `fantasy/rankings.md`. Do not reimplement the
formulas in JavaScript.

## Two lists, and a column

| Toggle | Answers | Source field |
|---|---|---|
| **Current** | what he has done, season to date | `current` / `currentRank` |
| **Projected** | what he will do, rest of season | `projected` / `projectedRank` |

And one column that is **not** a toggle:

| Column | Answers | Source field |
|---|---|---|
| **14 days** | what he has done *lately* | `form14.avg` (games in the cell's tooltip) |

⚠ **Last 14 days is a WINDOW on current value, not a third value** (CLAUDE.md rule 32),
and that is exactly why it is a column rather than a view. It shipped as a third toggle on
16 Nov 2026 and came straight back out the same day — a toggle gives the window its own
ranking, so "he is 12th" means two different things on two screens, which is the mixing the
rule forbids. Beside the season average in the same row it can only be read as what it is.

`build_site_data.py` still calls `R.add_form()` **twice**, at 7 and 14 days, and emits
`form7` and `form14` per player. Both are needed and they do different jobs:

- **`form7` drives every SIGNAL** — table, left rail and trade flags. 7 days is what
  `rankings.md` bands on and the only width the persistence rates in rule 32 were fitted
  against. There is one signal per player and nothing on the page can change it.
- **`form14` is the column, and only the column.** It never moves a label.

`form7` is also mirrored to the legacy top-level `signal` / `form` / `formGames` keys — an
older `app.js` against a newer `rankings.json` still renders rather than going blank.
⚠ `add_form()` mutates rows in place and only writes `form_rank` / `signal_thin` /
`sig_override_why` for players it reaches, so the second pass would inherit the first
pass's leftovers for anyone who drops out of the new window. The wipe between passes is
load-bearing — do not remove it.

⚠ **A ninth column costs width.** Adding this one pushed the table 66px past the viewport
at ~920px and re-clipped the Minutes column — the same failure as the first attempt at the
14-day view. Paid for with tighter cell padding (`0.55rem` → `0.46rem`) and an ellipsis cap
on the fantasy-team column (`.owner span`, 8.5rem, full name in the `title`), which is the
only text in a row that can be cut without losing a number. Two of the nine team names
truncate. **Re-measure `scrollWidth - clientWidth` before adding another column.**

Run it only once a slate is final — a live game corrupts season averages.

## Deploying

Live at **<https://nba-fantasy-rankings.vercel.app/>**.

Deployed from GitHub on Vercel with **Root Directory `site`**, preset *Other*, and build,
output and install commands all left empty. There is nothing to build; Vercel serves this
directory as-is and picks up `vercel.json` from here.

⚠ `rankings.json` is a static file, so **a local rebuild does not change the live site** —
the regenerated file has to be committed and pushed. Vercel redeploys on push.

## Local preview

```bash
cd site && python3 -m http.server 8000
```

`file://` will not work — `app.js` fetches `rankings.json`, which browsers block
cross-origin on the local filesystem.
