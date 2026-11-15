# Rankings site

Static, frontend-only. Four files, no framework, no build step, no API.

| File | What it is |
|---|---|
| `index.html` | The page |
| `styles.css` | Theme — tokens lifted from `eighthold.com/styles.css` so the two read as one system |
| `app.js` | Renders the tables, the projected/current toggle, search and the my-team filter |
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
