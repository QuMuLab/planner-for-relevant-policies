#! /bin/bash

set -e

EXPNAME="exp-issue276"

SEARCH1="default-default-issue276"
SEARCH2="default"

PROPERTY="memory"

CONFIGS="
    mas-hhh-1k
    mas-hhh-10k
    mas-hhh-50k
    mas-hhh-100k
    mas-mas-bisim
    mas-mas-dfp-200k
"

for CONFIG in $CONFIGS; do
    FIRST="$SEARCH1-$CONFIG"
    SECOND="$SEARCH2-$CONFIG"
    ./downward-reports.py $EXPNAME-eval -r scatter -a $PROPERTY -c "$FIRST,$SECOND"
done
