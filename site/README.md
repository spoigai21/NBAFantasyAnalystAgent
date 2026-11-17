# Rankings site

Static, frontend-only. Four files, no framework, no build step, no API.

| File | What it is |
|---|---|
| `index.html` | The page |
| `styles.css` | Theme — tokens lifted from `eighthold.com/styles.css` so the two read as one system |
| `app.js` | Renders the tables, the current / projected / last-14-days toggle, search and the my-team filter |
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

## The three views

| Toggle | Answers | Source field |
|---|---|---|
| **Current** | what he has done, season to date | `current` / `currentRank` |
| **Projected** | what he will do, rest of season | `projected` / `projectedRank` |
| **Last 14 days** | what he has done *lately* | `form14` |

⚠ **Last 14 days is a WINDOW on current value, not a third value** (CLAUDE.md rule 32).
Season-to-date and last-14-days both answer "what has he done"; projected is the only
forward number. The caption says so on screen so the distinction does not quietly collapse.

`build_site_data.py` calls `R.add_form()` **twice**, at 7 and 14 days, and emits `form7`
and `form14` per player. The shipped board bands on 7 days, so `form7` is also mirrored to
the legacy top-level `signal` / `form` / `formGames` keys — an older `app.js` against a
newer `rankings.json` still renders rather than going blank.
⚠ `add_form()` mutates rows in place and only writes `form_rank` / `signal_thin` /
`sig_override_why` for players it reaches, so the second pass would inherit the first
pass's leftovers for anyone who drops out of the new window. The wipe between passes is
load-bearing — do not remove it.

Whichever view is active drives the signal everywhere: table, left rail and trade flags.
LaMelo is the case that proves it — **BUY LOW at 14 days, FADE (minutes) at 7**.

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
