#! /bin/bash

set -e

if [[ "$#" != 1 ]]; then
    echo please specify phase:
    echo 1 -- build preprocess experiment
    echo 2 -- submit preprocess experiment
    echo 3 -- run resultfetcher on preprocess experiment
    echo 4 -- build main experiment
    echo 5 -- submit main experiment
    echo 6 -- run resultfetcher on main experiment
    echo 7 -- run reports
    exit 2
fi

PHASE=$1
EXPNAME=bjolpexp
CONFIGS=downward_configs.py:lmopt_rhw,downward_configs.py:lmopt_hm1
QUEUE=opteron_core.q

## For testing, use this:
SUITE=gripper:prob01.pddl,gripper:prob02.pddl
EXPTYPE=local

## For the real experiment, use this:
SUITE=OPTIMAL
EXPTYPE=gkigrid

EXPTYPEOPT="--exp-type $EXPTYPE"
if [[ "$EXPTYPE" == gkigrid ]]; then
    EXPTYPEOPT="$EXPTYPEOPT --queue $QUEUE"
elif [[ "$EXPTYPE" != local ]]; then
    echo unknown EXPTYPE: $EXPTYPE
    exit 2
fi

function build-all {
    pushd .
    cd ../src/
    ./build_all
    popd
}

if [[ "$PHASE" == 1 ]]; then
    build-all ## TODO: Shouldn't the scripts do that for us?
    ./downward_experiments.py --preprocess -s $SUITE $EXPTYPEOPT $EXPNAME
elif [[ "$PHASE" == 2 ]]; then
    if [[ "$EXPTYPE" == gkigrid ]]; then
        qsub ./$EXPNAME-p/$EXPNAME.q
    else
        ./$EXPNAME-p/run
    fi
elif [[ "$PHASE" == 3 ]]; then
    ./resultfetcher.py $EXPNAME-p
elif [[ "$PHASE" == 4 ]]; then
    build-all ## TODO: Shouldn't the scripts do that for us?
    ./downward_experiments.py -s $SUITE -c $CONFIGS $EXPTYPEOPT $EXPNAME
    # HACK! See issue195.
    cp ../src/search/{dispatch,downward-{1,2,4}} $EXPNAME/
elif [[ "$PHASE" == 5 ]]; then
    if [[ "$EXPTYPE" == gkigrid ]]; then
        qsub ./$EXPNAME/$EXPNAME.q
    else
        ./$EXPNAME/run
    fi
elif [[ "$PHASE" == 6 ]]; then
    ./downward-resultfetcher.py $EXPNAME
elif [[ "$PHASE" == 7 ]]; then
    ./downward-reports.py $EXPNAME-eval
else
    echo "unknown phase: $PHASE"
    exit 2
fi
