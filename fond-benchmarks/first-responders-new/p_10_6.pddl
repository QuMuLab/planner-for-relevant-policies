(define (problem FR_10_6)
 (:domain first-response)
 (:objects  l1 l2 l3 l4 l5 l6 l7 l8 l9 l10  - location
	    f1 f2 f3 f4 f5 f6 - fire_unit
	    v1 v2 v3 v4 v5 v6 - victim
	    m1 m2 - medical_unit
)
 (:init 
	;;strategic locations
     (hospital l5)
     (hospital l9)
     (hospital l9)
     (hospital l6)
     (hospital l3)
     (hospital l10)
     (hospital l5)
     (hospital l9)
     (hospital l6)
     (hospital l5)
     (water-at l1)
     (water-at l5)
     (water-at l7)
     (water-at l9)
     (water-at l7)
     (water-at l4)
	;;disaster info
     (fire l7)
     (victim-at v1 l10)
     (victim-status v1 dying)
     (fire l3)
     (victim-at v2 l7)
     (victim-status v2 hurt)
     (fire l9)
     (victim-at v3 l2)
     (victim-status v3 dying)
     (fire l7)
     (victim-at v4 l8)
     (victim-status v4 hurt)
     (fire l2)
     (victim-at v5 l4)
     (victim-status v5 hurt)
     (fire l10)
     (victim-at v6 l9)
     (victim-status v6 dying)
	;;map info
	(adjacent l1 l1)
	(adjacent l2 l2)
	(adjacent l3 l3)
	(adjacent l4 l4)
	(adjacent l5 l5)
	(adjacent l6 l6)
	(adjacent l7 l7)
	(adjacent l8 l8)
	(adjacent l9 l9)
	(adjacent l10 l10)
   (adjacent l1 l1)
   (adjacent l1 l1)
   (adjacent l1 l2)
   (adjacent l2 l1)
   (adjacent l1 l3)
   (adjacent l3 l1)
   (adjacent l1 l4)
   (adjacent l4 l1)
   (adjacent l2 l1)
   (adjacent l1 l2)
   (adjacent l2 l2)
   (adjacent l2 l2)
   (adjacent l4 l1)
   (adjacent l1 l4)
   (adjacent l4 l2)
   (adjacent l2 l4)
   (adjacent l5 l1)
   (adjacent l1 l5)
   (adjacent l6 l1)
   (adjacent l1 l6)
   (adjacent l6 l2)
   (adjacent l2 l6)
   (adjacent l6 l3)
   (adjacent l3 l6)
   (adjacent l6 l4)
   (adjacent l4 l6)
   (adjacent l6 l5)
   (adjacent l5 l6)
   (adjacent l7 l1)
   (adjacent l1 l7)
   (adjacent l7 l2)
   (adjacent l2 l7)
   (adjacent l7 l3)
   (adjacent l3 l7)
   (adjacent l7 l4)
   (adjacent l4 l7)
   (adjacent l7 l5)
   (adjacent l5 l7)
   (adjacent l8 l1)
   (adjacent l1 l8)
   (adjacent l8 l2)
   (adjacent l2 l8)
   (adjacent l8 l3)
   (adjacent l3 l8)
   (adjacent l8 l4)
   (adjacent l4 l8)
   (adjacent l8 l5)
   (adjacent l5 l8)
   (adjacent l9 l1)
   (adjacent l1 l9)
   (adjacent l9 l2)
   (adjacent l2 l9)
   (adjacent l9 l3)
   (adjacent l3 l9)
   (adjacent l9 l4)
   (adjacent l4 l9)
   (adjacent l10 l1)
   (adjacent l1 l10)
   (adjacent l10 l2)
   (adjacent l2 l10)
   (adjacent l10 l3)
   (adjacent l3 l10)
	(fire-unit-at f1 l10)
	(fire-unit-at f2 l1)
	(fire-unit-at f3 l4)
	(fire-unit-at f4 l4)
	(fire-unit-at f5 l1)
	(fire-unit-at f6 l5)
	(medical-unit-at m1 l10)
	(medical-unit-at m2 l8)
	)
 (:goal (and  (nfire l7) (nfire l3) (nfire l9) (nfire l7) (nfire l2) (nfire l10)  (victim-status v1 healthy) (victim-status v2 healthy) (victim-status v3 healthy) (victim-status v4 healthy) (victim-status v5 healthy) (victim-status v6 healthy)))
 )
