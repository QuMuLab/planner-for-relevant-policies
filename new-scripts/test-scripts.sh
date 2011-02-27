#! /bin/bash

rm -rf test-exp-p
rm -rf test-exp
rm -rf test-exp-eval

for STEP in {1..7}; do
    ./test-exp.sh $STEP
done
