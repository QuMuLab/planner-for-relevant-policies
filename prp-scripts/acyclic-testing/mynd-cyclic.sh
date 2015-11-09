#! /bin/bash

#/home/cjmuise/Projects/mynd/translator-fond/translate.py $1 $2
#java -Xmx1g -classpath /home/cjmuise/Projects/mynd/src mynd.MyNDPlanner -laostar -ff output.sas
/u/cjmuise/EXPERIMENTS/mynd/translator-fond/translate.py $1 $2
java -Xmx1g -classpath /u/cjmuise/EXPERIMENTS/mynd/src mynd.MyNDPlanner -laostar -ff output.sas
