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

function run-task-wrapped {
    CONFIG_NAME=$1
    PREPROCESSED_INPUT=$2
    MUTEX_FILE=$3
    PLANNER_EXECUTABLE=$4
    TIMEOUT=$5
    MEMORY_KB=$6
    shift 6
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
    echo Starting planner...
    cp $MUTEX_FILE all.groups
    (
	ulimit -c 0
	ulimit -t $TIMEOUT
	ulimit -v $MEMORY_KB
	$PLANNER_EXECUTABLE "$@" < $PREPROCESSED_INPUT
    ) > search.log 2> search.err
    echo exit code: $?
    times
    date
    rm -f all.groups
    echo Done.
}

function run-task {
    RESULT_DIR=$1
    shift
    echo [$1] $2...
    if [ -e $RESULT_DIR ]; then
	rm -r $RESULT_DIR
    fi
    mkdir -p $RESULT_DIR
    cd $RESULT_DIR
    run-task-wrapped "$@" > driver.log 2> driver.err
}

