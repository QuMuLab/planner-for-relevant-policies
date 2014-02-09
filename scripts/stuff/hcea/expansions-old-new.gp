#! /usr/bin/env gnuplot

set terminal png

set logscale x
set logscale y
set output "expansions-cC-yY-pointcloud.png"
set xlabel "expansions: cC"
set ylabel "expansions: yY"
plot "expansions-cC-yY.data" using 2:3 with points
reset

set logscale x
set logscale y
set output "expansions-cC-yY-factor.png"
set xlabel "expansions: cC"
set ylabel "factor of improvement"
set yrange [0.0001:10000]
plot "expansions-cC-yY.data" using 2:($2/$3) with points
reset

set logscale x
set logscale y
set output "expansions-aA-yY-pointcloud.png"
set xlabel "expansions: aA"
set ylabel "expansions: yY"
plot "expansions-aA-yY.data" using 2:3 with points
reset

set logscale x
set logscale y
set output "expansions-aA-yY-factor.png"
set xlabel "expansions: aA"
set ylabel "factor of improvement"
set yrange [0.0001:10000]
plot "expansions-aA-yY.data" using 2:($2/$3) with points
reset

set logscale x
set logscale y
set output "expansions-fF-yY-pointcloud.png"
set xlabel "expansions: fF"
set ylabel "expansions: yY"
plot "expansions-fF-yY.data" using 2:3 with points

set logscale x
set logscale y
set output "expansions-fF-yY-factor.png"
set xlabel "expansions: fF"
set ylabel "factor of improvement"
set yrange [0.0001:10000]
plot "expansions-fF-yY.data" using 2:($2/$3) with points
reset
