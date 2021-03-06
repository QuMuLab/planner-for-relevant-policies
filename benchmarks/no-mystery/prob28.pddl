(define
  (problem strips-mysty-x-28)
  (:domain no-mystery-strips)
  (:objects muellheim brombach denzlingen merdingen boetzingen
      daemonenrikscha kuechenmaschine halbgefrorenes gruenkohl
      faschiertes kapselheber kaesebaellchen wensleydale fuel-0 fuel-1
      fuel-2 fuel-3 fuel-4 fuel-5 fuel-6 fuel-7 capacity-0 capacity-1
      capacity-2)
  (:init
    (at daemonenrikscha muellheim)
    (at faschiertes denzlingen)
    (at gruenkohl brombach)
    (at halbgefrorenes brombach)
    (at kaesebaellchen merdingen)
    (at kapselheber denzlingen)
    (at kuechenmaschine muellheim)
    (at wensleydale boetzingen)
    (capacity daemonenrikscha capacity-2)
    (capacity-number capacity-0)
    (capacity-number capacity-1)
    (capacity-number capacity-2)
    (capacity-predecessor capacity-0 capacity-1)
    (capacity-predecessor capacity-1 capacity-2)
    (connected boetzingen brombach)
    (connected boetzingen merdingen)
    (connected boetzingen muellheim)
    (connected brombach boetzingen)
    (connected brombach muellheim)
    (connected denzlingen merdingen)
    (connected denzlingen muellheim)
    (connected merdingen boetzingen)
    (connected merdingen denzlingen)
    (connected muellheim boetzingen)
    (connected muellheim brombach)
    (connected muellheim denzlingen)
    (fuel boetzingen fuel-7)
    (fuel brombach fuel-6)
    (fuel denzlingen fuel-2)
    (fuel merdingen fuel-7)
    (fuel muellheim fuel-1)
    (fuel-number fuel-0)
    (fuel-number fuel-1)
    (fuel-number fuel-2)
    (fuel-number fuel-3)
    (fuel-number fuel-4)
    (fuel-number fuel-5)
    (fuel-number fuel-6)
    (fuel-number fuel-7)
    (fuel-predecessor fuel-0 fuel-1)
    (fuel-predecessor fuel-1 fuel-2)
    (fuel-predecessor fuel-2 fuel-3)
    (fuel-predecessor fuel-3 fuel-4)
    (fuel-predecessor fuel-4 fuel-5)
    (fuel-predecessor fuel-5 fuel-6)
    (fuel-predecessor fuel-6 fuel-7)
    (location boetzingen)
    (location brombach)
    (location denzlingen)
    (location merdingen)
    (location muellheim)
    (package faschiertes)
    (package gruenkohl)
    (package halbgefrorenes)
    (package kaesebaellchen)
    (package kapselheber)
    (package kuechenmaschine)
    (package wensleydale)
    (vehicle daemonenrikscha))
  (:goal
    (and
      (at faschiertes boetzingen)
      (at kaesebaellchen boetzingen))))
