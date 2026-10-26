#!/bin/bash
# Purge Josh Lloyd's transcripts from this repo's PUBLISHED GIT HISTORY.
#
# Why this is needed: removing a file from the current tree does not remove it from
# past commits. As of 26 Oct 2026 the raw transcripts were still fetchable from the
# public repo at an old SHA (verified: HTTP 200, 45,243 bytes), and every historical
# copy of fantasy/league.db contained the same 2,501 passages / ~291k words.
#
# Run from the repo root:  bash purge-transcripts-from-history.sh
#
# THIS REWRITES EVERY COMMIT SHA AND FORCE-PUSHES. Anyone who already cloned keeps
# their copy — a rewrite limits future exposure, it cannot un-publish the past.
# A full backup already exists (see BACKUP below); verify it before running.

set -euo pipefail
cd "$(dirname "$0")"

BACKUP=$(ls -d ~/Desktop/nbafantasy-backup-* 2>/dev/null | tail -1 || true)
PATHS=("fantasy/transcripts" "fantasy/league.db")

echo "repo:    $(pwd)"
echo "remote:  $(git remote get-url origin)"
echo "backup:  ${BACKUP:-NONE FOUND}"
echo "commits: $(git rev-list --count HEAD)"
echo
if [ -z "$BACKUP" ]; then
  echo "No backup found. Make one first:"
  echo "  git bundle create ~/Desktop/repo-backup.bundle --all"
  exit 1
fi
if [ -n "$(git status --porcelain)" ]; then
  echo "Working tree is not clean. Commit your staged changes first, then re-run:"
  git status --short
  exit 1
fi

echo "This will purge from ALL history:"
printf '  %s\n' "${PATHS[@]}"
echo
read -r -p 'Type REWRITE to continue: ' ok
[ "$ok" = "REWRITE" ] || { echo "aborted"; exit 1; }

# Keep the current, sanitised league.db aside — it is re-added after the rewrite.
TMP=$(mktemp -d)
cp fantasy/league.db "$TMP/league.db"

echo
echo "==> rewriting history"
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch --force --prune-empty \
  --index-filter 'git rm -r --cached --ignore-unmatch fantasy/transcripts fantasy/league.db' \
  --tag-name-filter cat -- --all

echo
echo "==> dropping the old refs and repacking"
rm -rf .git/refs/original
git reflog expire --expire=now --all
git gc --prune=now --aggressive --quiet

echo
echo "==> restoring the sanitised league.db as a fresh commit"
mkdir -p fantasy && cp "$TMP/league.db" fantasy/league.db && rm -rf "$TMP"
git add -f fantasy/league.db
git commit -q -m "Re-add league.db without the Lloyd transcript tables

Rebuilt history no longer carries any copy of the transcripts. This is our own
data only: players, game_log, transactions, research, game_grades, player_form,
name_aliases."

echo
echo "==> verifying NOTHING remains"
fail=0
n=$(git rev-list --all --objects -- 'fantasy/transcripts/*.txt' | grep -c '\.txt' || true)
echo "   transcript .txt blobs in history: $n  (want 0)"; [ "$n" = "0" ] || fail=1
n=$(git rev-list --all --objects -- 'fantasy/league.db' | grep -c 'league\.db' || true)
echo "   league.db blobs in history:       $n  (want 1, the clean one)"
for phrase in "free real estate" "Bazales" "claude-code session"; do
  hits=0
  while read -r sha; do
    [ -z "$sha" ] && continue
    if git cat-file -p "$sha" 2>/dev/null | strings | grep -qi "$phrase"; then
      hits=$((hits+1))
    fi
  done < <(git rev-list --all --objects -- 'fantasy/league.db' | awk '{print $1}')
  echo "   \"$phrase\" in any league.db blob: $hits"
done
[ "$fail" = "0" ] || { echo; echo "VERIFICATION FAILED — do not push."; exit 1; }

echo
echo "==> force-pushing"
read -r -p 'Type PUSH to force-push the rewritten history: ' ok2
[ "$ok2" = "PUSH" ] || { echo "stopped before push; history is rewritten locally only"; exit 0; }
git push --force-with-lease origin main

echo
echo "Done. Verify the old SHA is now a 404:"
echo "  curl -s -o /dev/null -w '%{http_code}\\n' \\"
echo "    https://raw.githubusercontent.com/spoigai21/NBAFantasyAnalystAgent/0717a05/fantasy/transcripts/2026-10-23_mailbag.txt"
echo
echo "GitHub caches unreachable objects for a while. To have them purged now, ask"
echo "GitHub Support to run gc on the repo, or delete and recreate the repo."
