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

if [[ "$(basename "$0")" == experiment.sh ]]; then
    echo "$(basename "$0") is supposed to be called from another script."
    echo "Are you running it as a main script?"
    exit 2
fi

if [[ "$#" != 1 ]]; then
    usage
fi

PHASE=$1

## You can set EXPNAME manually or it will be derived from the
## basename of the script that called this one.

if [[ -z $EXPNAME ]]; then
    EXPNAME="exp-$(basename "$0" .sh)"
fi

EXPTYPEOPT="--exp-type $EXPTYPE"
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

function build-all {
    pushd .
    cd ../src/
    ./build_all
    popd
}

if [[ "$PHASE" == 1 ]]; then
    build-all ## TODO: Shouldn't the scripts ensure that for us?
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
    build-all ## TODO: Shouldn't the scripts ensure that for us?
    ./downward_experiments.py -s $SUITE -c $CONFIGS $EXPTYPEOPT $EXPNAME
    # TODO/HACK! See issue195.
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
    ## TODO: The report script strip dashes out of the filename,
    ##       so exp-name-eval => expnameeval. Why?
    ./downward-reports.py $EXPNAME-eval
    ./downward-reports.py --res=problem $EXPNAME-eval
elif [[ "$PHASE" == 8 ]]; then
    BASEURL="http://www.informatik.uni-freiburg.de/~$(whoami)"
    if [[ "$(hostname)" == alfons ]]; then
        BASEDIR=/lummerland
    else
        BASEDIR=~
    fi
    echo "copying reports to .public_html -- to view, run:"
     ## TODO: we strip dashes, see above. We use sed since there
    ##        might be multiple occurrences.
    MODEXPNAME="$(echo "$EXPNAME" | sed -e 's/-//g')"
    for REPORT in "$MODEXPNAME"eval-{d,p}-abs.html; do
        cp "reports/$REPORT" "$BASEDIR/.public_html/"
        echo "firefox $BASEURL/$REPORT &"
    done
else
    echo "unknown phase: $PHASE"
    echo
    usage
fi
