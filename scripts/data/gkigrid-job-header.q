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
    REALCONFIG=$1
    PREPROCESSED_INPUT=$2
    PLANNER_EXECUTABLE=$3
    TIMEOUT=$4
    MEMORY_KB=$5
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
    (
	ulimit -c 0
	ulimit -t $TIMEOUT
	ulimit -v $MEMORY_KB
	$PLANNER_EXECUTABLE $REALCONFIG < $PREPROCESSED_INPUT
    ) > search.log 2> search.err
    echo exit code: $?
    times
    date
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

