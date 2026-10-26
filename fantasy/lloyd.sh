#!/bin/bash
# Everything Josh Lloyd said about a player, MOST RECENT FIRST.
# Expands auto-caption manglings automatically (Buzelis -> Bazales, Edey -> Edy, ...).
#   ./fantasy/lloyd.sh Buzelis          ./fantasy/lloyd.sh "Edey minutes" 10
#
# The transcript index lives in fantasy/lloyd.db, which is GITIGNORED — those are
# Josh Lloyd's words, not ours to redistribute under this repo's MIT licence.
# Rebuild it from fantasy/transcripts/ with: python3 fantasy/index_lloyd.py
[ -z "$1" ] && { echo 'usage: ./fantasy/lloyd.sh "<player or terms>" [limit]'; exit 1; }
[ -f fantasy/lloyd.db ] || { echo "fantasy/lloyd.db missing — run: python3 fantasy/index_lloyd.py"; exit 1; }
Q=$(printf '%s' "$1" | sed "s/'/''/g")
LIM=${2:-6}
EXP=$(sqlite3 fantasy/league.db "
  SELECT GROUP_CONCAT('\"'||alias||'\"',' OR ') FROM name_aliases
  WHERE hits>0 AND (player LIKE '%$Q%' OR alias LIKE '%$Q%');")
if [ -n "$EXP" ] && [ "$EXP" != "" ]; then
  MATCH="$EXP"; echo "# expanded to: $EXP"
else
  MATCH="$Q"
fi
sqlite3 fantasy/lloyd.db <<SQL
.mode line
SELECT s.show_date AS date, s.kind, s.text
FROM lloyd_fts f JOIN lloyd_segments s ON s.id=f.rowid
WHERE lloyd_fts MATCH '$MATCH'
ORDER BY s.show_date DESC, s.ordinal
LIMIT $LIM;
SQL
