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
./downward-reports.py $EXPNAME-eval -r any --min-value 10 --max-value 50 --step 15
./downward-reports.py $EXPNAME-eval -r suite --filter domain:eq:gripper --outfile exp_test_suite.py
./downward-reports.py $EXPNAME-eval -r rel --dry -a coverage --rel-change 0
./downward-reports.py $EXPNAME-eval -r scatter -a search_time
./downward-reports.py $EXPNAME-eval -r abs --dry --res problem -a expansions,landmarks,landmarks_generation_time #,initial_h_value
./downward-reports.py $EXPNAME-eval -r abs --dry -a search_time,coverage
