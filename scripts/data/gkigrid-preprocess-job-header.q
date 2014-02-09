#! /bin/bash
### Set shell.
#$ -S /bin/bash
### Don't send emails.
#$ -m n
### Execute job from current working directory.
#$ -cwd
### redirect stdout and stderr
#$ -e %(errfile)s
#$ -o %(logfile)s
### Set timeout.
#$ -l h_cpu=%(driver_timeout)d
### Set queue (athlon_core.q => one core; athlon.q => whole CPU).
#$ -q athlon_core.q
### Number of tasks
#$ -t 1-%(num_tasks)d

function delete-if-empty {
    if [[ -f "$1" && ! -s "$1" ]]; then
        rm "$1"
    fi
}

function translate-wrapped {
    TRANSLATOR_EXECUTABLE=$1
    TIMEOUT=$2
    PDDL_DOMAIN=$3
    PDDL_PROBLEM=$4
    pwd
    date
    hostname
    echo
    ulimit -a
    echo
    echo CPU info:
    cat /proc/cpuinfo
    echo
    echo meminfo:
    cat /proc/meminfo
    echo
    echo Starting translator...
    (
	ulimit -c 0
	ulimit -t $TIMEOUT
	$TRANSLATOR_EXECUTABLE $PDDL_DOMAIN $PDDL_PROBLEM
    ) > translate.log 2> translate.err
    delete-if-empty translate.err
    echo exit code: $?
    times
    date
    echo Done.
}

function preprocess-wrapped {
    PREPROCESSOR_EXECUTABLE=$1
    TIMEOUT=$2
    TRANSLATE_DIR=$3
    pwd
    date
    hostname
    echo
    ulimit -a
    echo
    echo CPU info:
    cat /proc/cpuinfo
    echo
    echo meminfo:
    cat /proc/meminfo
    echo
    echo Starting preprocessor...
    (
	ulimit -c 0
	ulimit -t $TIMEOUT
	$PREPROCESSOR_EXECUTABLE < "$TRANSLATE_DIR/output.sas"
    ) > preprocess.log 2> preprocess.err
    delete-if-empty preprocess.err
    echo exit code: $?
    times
    date
    echo Done.
}

function preprocess-task {
    PDDL_DOMAIN=$1
    PDDL_PROBLEM=$2
    TRANSLATOR_EXECUTABLE=$3
    TRANSLATOR_TIMEOUT=$4
    TRANSLATE_DIR=$5
    PREPROCESSOR_EXECUTABLE=$6
    PREPROCESSOR_TIMEOUT=$7
    PREPROCESS_DIR=$8

    echo [translate] $PDDL_DOMAIN/$PDDL_PROBLEM...
    if [ -e "$TRANSLATE_DIR" ]; then
	rm -r "$TRANSLATE_DIR"
    fi
    mkdir -p "$TRANSLATE_DIR"
    cd "$TRANSLATE_DIR"
    translate-wrapped "$TRANSLATOR_EXECUTABLE" "$TRANSLATOR_TIMEOUT" \
        "$PDDL_DOMAIN" "$PDDL_PROBLEM" > driver.log 2> driver.err
    delete-if-empty driver.err

    echo [preprocess] $PDDL_DOMAIN/$PDDL_PROBLEM...
    if [ -e "$PREPROCESS_DIR" ]; then
	rm -r "$PREPROCESS_DIR"
    fi
    mkdir -p "$PREPROCESS_DIR"
    cd "$PREPROCESS_DIR"
    preprocess-wrapped "$PREPROCESSOR_EXECUTABLE" "$PREPROCESSOR_TIMEOUT" \
        "$TRANSLATE_DIR" > driver.log 2> driver.err
    delete-if-empty driver.err
}

