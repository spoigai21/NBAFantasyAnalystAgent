#!/bin/bash
# Query the league DB.  ./fantasy/q.sh "SELECT ..."   or no args for the cheat sheet
[ -z "$1" ] && { cat <<'H'
fantasy/league.db  — players, game_log, transactions, research, game_grades,
                     player_form, name_aliases
fantasy/lloyd.db   — lloyd_segments, lloyd_fts, lloyd_quotes  (GITIGNORED: Lloyd's
                     own words; attached below as lloyddb so queries still work)

  ./fantasy/q.sh "SELECT name,per_game,proj_full,delta FROM players
                  WHERE fantasy_team='The Freaky Alien' ORDER BY delta"
  ./fantasy/q.sh "SELECT show_date,quote FROM lloyd_quotes WHERE player LIKE '%Edey%'
                  ORDER BY show_date DESC LIMIT 3"
  ./fantasy/q.sh "SELECT topic,finding FROM research WHERE player='Zach LaVine'"
  ./fantasy/q.sh "SELECT fantasy_team, ROUND(SUM(total)) t FROM players
                  GROUP BY 1 ORDER BY t DESC"
H
exit 0; }
ATT=""
[ -f fantasy/lloyd.db ] && ATT="ATTACH DATABASE 'fantasy/lloyd.db' AS lloyddb;"
sqlite3 -header -column fantasy/league.db "$ATT$1"
