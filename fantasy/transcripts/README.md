# Raw Josh Lloyd / Locked On transcripts — LOCAL ONLY

**The transcripts themselves are not in this repo and never will be.** They are Josh
Lloyd's copyrighted work; this repo is MIT, and that licence is not ours to apply to
his words. `*.txt` here and `fantasy/lloyd.db` are both gitignored, and were purged
from git history on 26 Oct 2026.

This directory is empty on a fresh clone. That is expected.

## What depends on it

| Tool | Needs |
|---|---|
| `./fantasy/lloyd.sh <player>` | `fantasy/lloyd.db` |
| `python3 fantasy/verify.py quote "..."` | `fantasy/lloyd.db` |
| `python3 fantasy/aliases.py` | `fantasy/lloyd.db` |

Each fails with a clear message rather than returning silently empty — which matters,
because a zero-hit search looks identical to "he never said anything," and that is
exactly how a fabricated quote got attributed to Lloyd on 23 Oct 2026 and acted on for
two days.

## Rebuilding locally

Drop the transcript `.txt` files in here, then:

```
python3 fantasy/index_lloyd.py     # builds fantasy/lloyd.db (segments + FTS5)
python3 fantasy/aliases.py         # maps caption manglings -> real names
```

## Why the alias table exists

The auto-captioner mangles proper nouns badly. **21 of the league's biggest names return
zero hits on their real surname** — Doncic is "Luca", Antetokounmpo is "Giannis",
Haliburton is "Hallebertton", Wembanyama is "Wemi", Edey is "Edy", Buzelis is "Bazales",
Murray is "Dejonte". Always search via `lloyd.sh`, never a bare grep.

## Rule: grep the raw transcript before saying evidence is missing

The `~/Desktop/lloyd_*.md` summaries are lossy and stale. They are an index, not the
record, and at least one quote in them is fabricated.
