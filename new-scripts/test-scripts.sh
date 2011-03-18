#! /bin/bash
set -e

EXPNAME=test-exp

rm -rf $EXPNAME-p
rm -rf $EXPNAME
rm -rf $EXPNAME-eval

for STEP in {1..7}; do
    ./test-exp.sh $STEP
done

./downward-reports-ipc.py $EXPNAME-eval coverage
