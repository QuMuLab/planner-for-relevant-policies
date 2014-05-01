(define (problem FR_8_4)
 (:domain first-response)
 (:objects  l1 l2 l3 l4 l5 l6 l7 l8  - location
	    f1 f2 f3 f4 f5 f6 f7 - fire_unit
	    v1 v2 v3 v4 - victim
	    m1 m2 m3 m4 m5 - medical_unit
)
 (:init 
	;;strategic locations
     (hospital l1)
     (hospital l6)
     (hospital l3)
     (water-at l6)
     (water-at l2)
     (water-at l7)
     (water-at l3)
     (water-at l8)
     (water-at l5)
     (water-at l1)
	;;disaster info
     (fire l6)
     (victim-at v1 l3)
     (victim-status v1 dying)
     (fire l5)
     (victim-at v2 l2)
     (victim-status v2 dying)
     (fire l5)
     (victim-at v3 l2)
     (victim-status v3 hurt)
     (fire l4)
     (victim-at v4 l1)
     (victim-status v4 hurt)
	;;map info
	(adjacent l1 l1)
	(adjacent l2 l2)
	(adjacent l3 l3)
	(adjacent l4 l4)
	(adjacent l5 l5)
	(adjacent l6 l6)
	(adjacent l7 l7)
	(adjacent l8 l8)
   (adjacent l1 l1)
   (adjacent l1 l1)
   (adjacent l1 l2)
   (adjacent l2 l1)
   (adjacent l1 l3)
   (adjacent l3 l1)
   (adjacent l2 l1)
   (adjacent l1 l2)
   (adjacent l4 l1)
   (adjacent l1 l4)
   (adjacent l4 l2)
   (adjacent l2 l4)
   (adjacent l4 l3)
   (adjacent l3 l4)
   (adjacent l4 l4)
   (adjacent l4 l4)
   (adjacent l4 l5)
   (adjacent l5 l4)
   (adjacent l4 l6)
   (adjacent l6 l4)
   (adjacent l5 l1)
   (adjacent l1 l5)
   (adjacent l5 l2)
   (adjacent l2 l5)
   (adjacent l5 l3)
   (adjacent l3 l5)
   (adjacent l5 l4)
   (adjacent l4 l5)
   (adjacent l6 l1)
   (adjacent l1 l6)
   (adjacent l6 l2)
   (adjacent l2 l6)
   (adjacent l6 l3)
   (adjacent l3 l6)
   (adjacent l7 l1)
   (adjacent l1 l7)
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
   (adjacent l8 l6)
   (adjacent l6 l8)
   (adjacent l8 l7)
   (adjacent l7 l8)
	(fire-unit-at f1 l6)
	(fire-unit-at f2 l3)
	(fire-unit-at f3 l8)
	(fire-unit-at f4 l4)
	(fire-unit-at f5 l1)
	(fire-unit-at f6 l6)
	(fire-unit-at f7 l2)
	(medical-unit-at m1 l7)
	(medical-unit-at m2 l3)
	(medical-unit-at m3 l8)
	(medical-unit-at m4 l5)
	(medical-unit-at m5 l1)
	)
 (:goal (and  (nfire l6) (nfire l5) (nfire l5) (nfire l4)  (victim-status v1 healthy) (victim-status v2 healthy) (victim-status v3 healthy) (victim-status v4 healthy)))
 )
