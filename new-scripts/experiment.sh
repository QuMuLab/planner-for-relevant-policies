#! /bin/bash
set -e

function usage() {
    echo "usage:"
    echo "    $(basename "$0") PHASE"
    echo "where PHASE is one of:"
    echo "1: build preprocess experiment"
    echo "2: submit preprocess experiment"
    echo "3: run resultfetcher on preprocess experiment"
    echo "4: build main experiment"
    echo "5: submit main experiment"
    echo "6: run resultfetcher on main experiment"
    echo "7: run reports"
    echo "8: copy reports to .public_html and print URL"
    exit 2
}

function run_experiment() {
    if [[ "$EXPTYPE" == gkigrid ]]; then
        pushd .
        cd $1
        if [ -e already-submitted ]; then
            # file exists
            echo "Experiment has already been submitted once. \
Delete the file 'already-submitted' or submit it \
manually if you know what you're doing."
        else
            qsub $1.q
            # Do not submit an experiment more than once
            touch already-submitted
        fi
        popd
    else
        ./$1/run
    fi
}

if [[ "$(basename "$0")" == experiment.sh ]]; then
    echo "$(basename "$0") is supposed to be called from another script."
    echo "Are you running it as a main script?"
    exit 2
fi

if [[ "$#" != 1 ]]; then
    usage
fi

PHASE=$1

# Support specifying an attribute subset e.g. "-a coverage,plan_length"
if [[ -z $REPORTATTRS ]]; then
    REPORTATTRS=""
fi

# Support specifying the module that is used for experiment creation.
# This is useful for the issue*.py scripts.
if [[ -z $EXPMODULE ]]; then
    EXPMODULE=downward_experiments.py
fi

# Support specifying various experiment options.
if [[ -z $EXPOPTS ]]; then
    EXPOPTS=""
fi

## You can set EXPNAME manually or it will be derived from the
## basename of the script that called this one.
if [[ -z $EXPNAME ]]; then
    EXPNAME="exp-$(basename "$0" .sh)"
fi

EXPTYPEOPT="$EXPTYPE"
if [[ "$EXPTYPE" == gkigrid ]]; then
    if [[ -z "$QUEUE" ]]; then
        echo error: must specify QUEUE
        exit 2
    fi
    EXPTYPEOPT="$EXPTYPEOPT --queue $QUEUE"
elif [[ "$EXPTYPE" != local ]]; then
    echo unknown EXPTYPE: $EXPTYPE
    exit 2
fi


if [[ "$PHASE" == 1 ]]; then
    ./$EXPMODULE --preprocess -s $SUITE --path $EXPNAME $EXPTYPEOPT
elif [[ "$PHASE" == 2 ]]; then
    run_experiment $EXPNAME-p
elif [[ "$PHASE" == 3 ]]; then
    ./resultfetcher.py $EXPNAME-p
elif [[ "$PHASE" == 4 ]]; then
    ./$EXPMODULE -s $SUITE -c $CONFIGS --path $EXPNAME $EXPOPTS $EXPTYPEOPT
elif [[ "$PHASE" == 5 ]]; then
    run_experiment $EXPNAME
elif [[ "$PHASE" == 6 ]]; then
    ./downward-resultfetcher.py $EXPNAME
elif [[ "$PHASE" == 7 ]]; then
    ./downward-reports.py $EXPNAME-eval $REPORTATTRS
    ./downward-reports.py --res=problem $EXPNAME-eval $REPORTATTRS
elif [[ "$PHASE" == 8 ]]; then
    BASEURL="http://www.informatik.uni-freiburg.de/~$(whoami)"
    if [[ "$(hostname)" == alfons ]]; then
        BASEDIR=/lummerland
    else
        BASEDIR=~
    fi
    echo "copying reports to .public_html -- to view, run:"
    for REPORT in "$EXPNAME"-eval-abs-{d,p}.html; do
        cp "reports/$REPORT" "$BASEDIR/.public_html/"
        echo "firefox $BASEURL/$REPORT &"
    done
else
    echo "unknown phase: $PHASE"
    echo
    usage
fi
