#!/bin/bash
# One command for everything we know about a player. START HERE for any player question.
#   ./fantasy/p.sh buzelis        ./fantasy/p.sh amen --lloyd 6    ./fantasy/p.sh garland --q turnovers
exec python3 "$(dirname "$0")/player.py" "$@"
