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

Vercel, with this directory as the project root:

```bash
cd site && vercel --prod
```

There is nothing to build; Vercel serves the directory as-is.

## Local preview

```bash
cd site && python3 -m http.server 8000
```

`file://` will not work — `app.js` fetches `rankings.json`, which browsers block
cross-origin on the local filesystem.
