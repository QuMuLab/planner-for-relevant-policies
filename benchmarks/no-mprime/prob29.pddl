(define
  (problem strips-mprime-x-29)
  (:domain no-mystery-prime-strips)
  (:objects riedlingen emmendingen lauchringen endingen kandern auggen
      freiburg kleinkems trollwagen kuebelwagen leipziger-allerlei
      halbgefrorenes terrorist taschenrechner grobe-bratwurst
      weihnachtsbaum donnerkiesel nichts pinkel fleisch eisbein fuel-0
      fuel-1 fuel-2 fuel-3 fuel-4 fuel-5 fuel-6 fuel-7 fuel-8
      capacity-0 capacity-1 capacity-2 capacity-3)
  (:init
    (at donnerkiesel auggen)
    (at eisbein kleinkems)
    (at fleisch kleinkems)
    (at grobe-bratwurst lauchringen)
    (at halbgefrorenes emmendingen)
    (at kuebelwagen kleinkems)
    (at leipziger-allerlei riedlingen)
    (at nichts auggen)
    (at pinkel freiburg)
    (at taschenrechner lauchringen)
    (at terrorist emmendingen)
    (at trollwagen emmendingen)
    (at weihnachtsbaum lauchringen)
    (capacity kuebelwagen capacity-3)
    (capacity trollwagen capacity-3)
    (capacity-number capacity-0)
    (capacity-number capacity-1)
    (capacity-number capacity-2)
    (capacity-number capacity-3)
    (capacity-predecessor capacity-0 capacity-1)
    (capacity-predecessor capacity-1 capacity-2)
    (capacity-predecessor capacity-2 capacity-3)
    (connected auggen endingen)
    (connected auggen freiburg)
    (connected auggen lauchringen)
    (connected emmendingen kleinkems)
    (connected emmendingen lauchringen)
    (connected endingen auggen)
    (connected endingen riedlingen)
    (connected freiburg auggen)
    (connected freiburg kleinkems)
    (connected kandern kleinkems)
    (connected kandern riedlingen)
    (connected kleinkems emmendingen)
    (connected kleinkems freiburg)
    (connected kleinkems kandern)
    (connected lauchringen auggen)
    (connected lauchringen emmendingen)
    (connected riedlingen endingen)
    (connected riedlingen kandern)
    (fuel auggen fuel-7)
    (fuel emmendingen fuel-6)
    (fuel endingen fuel-5)
    (fuel freiburg fuel-2)
    (fuel kandern fuel-0)
    (fuel kleinkems fuel-5)
    (fuel lauchringen fuel-8)
    (fuel riedlingen fuel-3)
    (fuel-number fuel-0)
    (fuel-number fuel-1)
    (fuel-number fuel-2)
    (fuel-number fuel-3)
    (fuel-number fuel-4)
    (fuel-number fuel-5)
    (fuel-number fuel-6)
    (fuel-number fuel-7)
    (fuel-number fuel-8)
    (fuel-predecessor fuel-0 fuel-1)
    (fuel-predecessor fuel-1 fuel-2)
    (fuel-predecessor fuel-2 fuel-3)
    (fuel-predecessor fuel-3 fuel-4)
    (fuel-predecessor fuel-4 fuel-5)
    (fuel-predecessor fuel-5 fuel-6)
    (fuel-predecessor fuel-6 fuel-7)
    (fuel-predecessor fuel-7 fuel-8)
    (location auggen)
    (location emmendingen)
    (location endingen)
    (location freiburg)
    (location kandern)
    (location kleinkems)
    (location lauchringen)
    (location riedlingen)
    (package donnerkiesel)
    (package eisbein)
    (package fleisch)
    (package grobe-bratwurst)
    (package halbgefrorenes)
    (package leipziger-allerlei)
    (package nichts)
    (package pinkel)
    (package taschenrechner)
    (package terrorist)
    (package weihnachtsbaum)
    (vehicle kuebelwagen)
    (vehicle trollwagen))
  (:goal
    (and
      (at eisbein auggen)
      (at nichts auggen))))
