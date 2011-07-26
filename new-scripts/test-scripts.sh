#! /bin/bash
set -e

EXPNAME=exp-test

rm -rf $EXPNAME-p
rm -rf $EXPNAME
rm -rf $EXPNAME-eval

for STEP in {1..7}; do
    ./test-exp.sh $STEP
    if [[ "$(hostname)" == habakuk && ($STEP == 2 || $STEP == 5) ]]; then
        echo Waiting for job to end
        sleep 10
    fi
done

./downward-reports-ipc.py $EXPNAME-eval coverage
