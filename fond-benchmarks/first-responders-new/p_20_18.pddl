(define (problem FR_20_18)
 (:domain first-response)
 (:objects  l1 l2 l3 l4 l5 l6 l7 l8 l9 l10 l11 l12 l13 l14 l15 l16 l17 l18 l19 l20  - location
	    f1 f2 f3 f4 f5 f6 f7 f8 f9 f10 f11 f12 - fire_unit
	    v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 v11 v12 v13 v14 v15 v16 v17 v18 - victim
	    m1 m2 m3 m4 m5 m6 m7 m8 m9 m10 m11 m12 m13 m14 m15 m16 m17 m18 m19 m20 - medical_unit
)
 (:init 
	;;strategic locations
     (hospital l2)
     (hospital l10)
     (hospital l12)
     (hospital l9)
     (hospital l4)
     (hospital l2)
     (hospital l7)
     (hospital l14)
     (hospital l17)
     (hospital l4)
     (hospital l3)
     (water-at l1)
     (water-at l5)
     (water-at l3)
     (water-at l8)
     (water-at l17)
     (water-at l16)
     (water-at l18)
     (water-at l15)
	;;disaster info
     (fire l15)
     (victim-at v1 l19)
     (victim-status v1 hurt)
     (fire l10)
     (victim-at v2 l13)
     (victim-status v2 dying)
     (fire l13)
     (victim-at v3 l7)
     (victim-status v3 dying)
     (fire l8)
     (victim-at v4 l6)
     (victim-status v4 dying)
     (fire l18)
     (victim-at v5 l14)
     (victim-status v5 hurt)
     (fire l16)
     (victim-at v6 l19)
     (victim-status v6 dying)
     (fire l16)
     (victim-at v7 l2)
     (victim-status v7 dying)
     (fire l4)
     (victim-at v8 l19)
     (victim-status v8 dying)
     (fire l20)
     (victim-at v9 l2)
     (victim-status v9 hurt)
     (fire l13)
     (victim-at v10 l1)
     (victim-status v10 dying)
     (fire l18)
     (victim-at v11 l19)
     (victim-status v11 hurt)
     (fire l7)
     (victim-at v12 l17)
     (victim-status v12 dying)
     (fire l19)
     (victim-at v13 l17)
     (victim-status v13 hurt)
     (fire l3)
     (victim-at v14 l13)
     (victim-status v14 hurt)
     (fire l4)
     (victim-at v15 l18)
     (victim-status v15 dying)
     (fire l4)
     (victim-at v16 l10)
     (victim-status v16 hurt)
     (fire l18)
     (victim-at v17 l16)
     (victim-status v17 hurt)
     (fire l8)
     (victim-at v18 l20)
     (victim-status v18 hurt)
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
	(adjacent l11 l11)
	(adjacent l12 l12)
	(adjacent l13 l13)
	(adjacent l14 l14)
	(adjacent l15 l15)
	(adjacent l16 l16)
	(adjacent l17 l17)
	(adjacent l18 l18)
	(adjacent l19 l19)
	(adjacent l20 l20)
   (adjacent l1 l1)
   (adjacent l1 l1)
   (adjacent l1 l2)
   (adjacent l2 l1)
   (adjacent l1 l3)
   (adjacent l3 l1)
   (adjacent l2 l1)
   (adjacent l1 l2)
   (adjacent l2 l2)
   (adjacent l2 l2)
   (adjacent l2 l3)
   (adjacent l3 l2)
   (adjacent l2 l4)
   (adjacent l4 l2)
   (adjacent l2 l5)
   (adjacent l5 l2)
   (adjacent l2 l6)
   (adjacent l6 l2)
   (adjacent l2 l7)
   (adjacent l7 l2)
   (adjacent l2 l8)
   (adjacent l8 l2)
   (adjacent l2 l9)
   (adjacent l9 l2)
   (adjacent l2 l10)
   (adjacent l10 l2)
   (adjacent l2 l11)
   (adjacent l11 l2)
   (adjacent l2 l12)
   (adjacent l12 l2)
   (adjacent l2 l13)
   (adjacent l13 l2)
   (adjacent l2 l14)
   (adjacent l14 l2)
   (adjacent l2 l15)
   (adjacent l15 l2)
   (adjacent l2 l16)
   (adjacent l16 l2)
   (adjacent l3 l1)
   (adjacent l1 l3)
   (adjacent l3 l2)
   (adjacent l2 l3)
   (adjacent l3 l3)
   (adjacent l3 l3)
   (adjacent l3 l4)
   (adjacent l4 l3)
   (adjacent l3 l5)
   (adjacent l5 l3)
   (adjacent l3 l6)
   (adjacent l6 l3)
   (adjacent l3 l7)
   (adjacent l7 l3)
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
   (adjacent l4 l7)
   (adjacent l7 l4)
   (adjacent l4 l8)
   (adjacent l8 l4)
   (adjacent l4 l9)
   (adjacent l9 l4)
   (adjacent l4 l10)
   (adjacent l10 l4)
   (adjacent l4 l11)
   (adjacent l11 l4)
   (adjacent l4 l12)
   (adjacent l12 l4)
   (adjacent l4 l13)
   (adjacent l13 l4)
   (adjacent l4 l14)
   (adjacent l14 l4)
   (adjacent l4 l15)
   (adjacent l15 l4)
   (adjacent l5 l1)
   (adjacent l1 l5)
   (adjacent l5 l2)
   (adjacent l2 l5)
   (adjacent l5 l3)
   (adjacent l3 l5)
   (adjacent l5 l4)
   (adjacent l4 l5)
   (adjacent l5 l5)
   (adjacent l5 l5)
   (adjacent l5 l6)
   (adjacent l6 l5)
   (adjacent l6 l1)
   (adjacent l1 l6)
   (adjacent l6 l2)
   (adjacent l2 l6)
   (adjacent l6 l3)
   (adjacent l3 l6)
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
   (adjacent l7 l6)
   (adjacent l6 l7)
   (adjacent l7 l7)
   (adjacent l7 l7)
   (adjacent l7 l8)
   (adjacent l8 l7)
   (adjacent l7 l9)
   (adjacent l9 l7)
   (adjacent l7 l10)
   (adjacent l10 l7)
   (adjacent l7 l11)
   (adjacent l11 l7)
   (adjacent l7 l12)
   (adjacent l12 l7)
   (adjacent l7 l13)
   (adjacent l13 l7)
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
   (adjacent l8 l8)
   (adjacent l8 l8)
   (adjacent l8 l9)
   (adjacent l9 l8)
   (adjacent l8 l10)
   (adjacent l10 l8)
   (adjacent l8 l11)
   (adjacent l11 l8)
   (adjacent l8 l12)
   (adjacent l12 l8)
   (adjacent l8 l13)
   (adjacent l13 l8)
   (adjacent l8 l14)
   (adjacent l14 l8)
   (adjacent l9 l1)
   (adjacent l1 l9)
   (adjacent l9 l2)
   (adjacent l2 l9)
   (adjacent l9 l3)
   (adjacent l3 l9)
   (adjacent l9 l4)
   (adjacent l4 l9)
   (adjacent l9 l5)
   (adjacent l5 l9)
   (adjacent l9 l6)
   (adjacent l6 l9)
   (adjacent l9 l7)
   (adjacent l7 l9)
   (adjacent l9 l8)
   (adjacent l8 l9)
   (adjacent l9 l9)
   (adjacent l9 l9)
   (adjacent l10 l1)
   (adjacent l1 l10)
   (adjacent l11 l1)
   (adjacent l1 l11)
   (adjacent l11 l2)
   (adjacent l2 l11)
   (adjacent l11 l3)
   (adjacent l3 l11)
   (adjacent l11 l4)
   (adjacent l4 l11)
   (adjacent l11 l5)
   (adjacent l5 l11)
   (adjacent l11 l6)
   (adjacent l6 l11)
   (adjacent l11 l7)
   (adjacent l7 l11)
   (adjacent l11 l8)
   (adjacent l8 l11)
   (adjacent l11 l9)
   (adjacent l9 l11)
   (adjacent l12 l1)
   (adjacent l1 l12)
   (adjacent l12 l2)
   (adjacent l2 l12)
   (adjacent l12 l3)
   (adjacent l3 l12)
   (adjacent l12 l4)
   (adjacent l4 l12)
   (adjacent l12 l5)
   (adjacent l5 l12)
   (adjacent l12 l6)
   (adjacent l6 l12)
   (adjacent l12 l7)
   (adjacent l7 l12)
   (adjacent l13 l1)
   (adjacent l1 l13)
   (adjacent l13 l2)
   (adjacent l2 l13)
   (adjacent l13 l3)
   (adjacent l3 l13)
   (adjacent l13 l4)
   (adjacent l4 l13)
   (adjacent l13 l5)
   (adjacent l5 l13)
   (adjacent l13 l6)
   (adjacent l6 l13)
   (adjacent l13 l7)
   (adjacent l7 l13)
   (adjacent l13 l8)
   (adjacent l8 l13)
   (adjacent l13 l9)
   (adjacent l9 l13)
   (adjacent l14 l1)
   (adjacent l1 l14)
   (adjacent l14 l2)
   (adjacent l2 l14)
   (adjacent l14 l3)
   (adjacent l3 l14)
   (adjacent l14 l4)
   (adjacent l4 l14)
   (adjacent l14 l5)
   (adjacent l5 l14)
   (adjacent l14 l6)
   (adjacent l6 l14)
   (adjacent l14 l7)
   (adjacent l7 l14)
   (adjacent l14 l8)
   (adjacent l8 l14)
   (adjacent l14 l9)
   (adjacent l9 l14)
   (adjacent l14 l10)
   (adjacent l10 l14)
   (adjacent l14 l11)
   (adjacent l11 l14)
   (adjacent l14 l12)
   (adjacent l12 l14)
   (adjacent l14 l13)
   (adjacent l13 l14)
   (adjacent l14 l14)
   (adjacent l14 l14)
   (adjacent l14 l15)
   (adjacent l15 l14)
   (adjacent l14 l16)
   (adjacent l16 l14)
   (adjacent l14 l17)
   (adjacent l17 l14)
   (adjacent l14 l18)
   (adjacent l18 l14)
   (adjacent l14 l19)
   (adjacent l19 l14)
   (adjacent l15 l1)
   (adjacent l1 l15)
   (adjacent l15 l2)
   (adjacent l2 l15)
   (adjacent l15 l3)
   (adjacent l3 l15)
   (adjacent l15 l4)
   (adjacent l4 l15)
   (adjacent l15 l5)
   (adjacent l5 l15)
   (adjacent l16 l1)
   (adjacent l1 l16)
   (adjacent l16 l2)
   (adjacent l2 l16)
   (adjacent l16 l3)
   (adjacent l3 l16)
   (adjacent l16 l4)
   (adjacent l4 l16)
   (adjacent l17 l1)
   (adjacent l1 l17)
   (adjacent l17 l2)
   (adjacent l2 l17)
   (adjacent l17 l3)
   (adjacent l3 l17)
   (adjacent l17 l4)
   (adjacent l4 l17)
   (adjacent l17 l5)
   (adjacent l5 l17)
   (adjacent l17 l6)
   (adjacent l6 l17)
   (adjacent l17 l7)
   (adjacent l7 l17)
   (adjacent l17 l8)
   (adjacent l8 l17)
   (adjacent l17 l9)
   (adjacent l9 l17)
   (adjacent l17 l10)
   (adjacent l10 l17)
   (adjacent l17 l11)
   (adjacent l11 l17)
   (adjacent l18 l1)
   (adjacent l1 l18)
   (adjacent l18 l2)
   (adjacent l2 l18)
   (adjacent l18 l3)
   (adjacent l3 l18)
   (adjacent l18 l4)
   (adjacent l4 l18)
   (adjacent l18 l5)
   (adjacent l5 l18)
   (adjacent l18 l6)
   (adjacent l6 l18)
   (adjacent l18 l7)
   (adjacent l7 l18)
   (adjacent l18 l8)
   (adjacent l8 l18)
   (adjacent l18 l9)
   (adjacent l9 l18)
   (adjacent l19 l1)
   (adjacent l1 l19)
   (adjacent l19 l2)
   (adjacent l2 l19)
   (adjacent l19 l3)
   (adjacent l3 l19)
   (adjacent l19 l4)
   (adjacent l4 l19)
   (adjacent l19 l5)
   (adjacent l5 l19)
   (adjacent l19 l6)
   (adjacent l6 l19)
   (adjacent l19 l7)
   (adjacent l7 l19)
   (adjacent l19 l8)
   (adjacent l8 l19)
   (adjacent l19 l9)
   (adjacent l9 l19)
   (adjacent l19 l10)
   (adjacent l10 l19)
   (adjacent l19 l11)
   (adjacent l11 l19)
   (adjacent l19 l12)
   (adjacent l12 l19)
   (adjacent l19 l13)
   (adjacent l13 l19)
   (adjacent l19 l14)
   (adjacent l14 l19)
   (adjacent l19 l15)
   (adjacent l15 l19)
   (adjacent l19 l16)
   (adjacent l16 l19)
   (adjacent l19 l17)
   (adjacent l17 l19)
   (adjacent l19 l18)
   (adjacent l18 l19)
   (adjacent l19 l19)
   (adjacent l19 l19)
   (adjacent l20 l1)
   (adjacent l1 l20)
   (adjacent l20 l2)
   (adjacent l2 l20)
   (adjacent l20 l3)
   (adjacent l3 l20)
   (adjacent l20 l4)
   (adjacent l4 l20)
   (adjacent l20 l5)
   (adjacent l5 l20)
   (adjacent l20 l6)
   (adjacent l6 l20)
   (adjacent l20 l7)
   (adjacent l7 l20)
   (adjacent l20 l8)
   (adjacent l8 l20)
   (adjacent l20 l9)
   (adjacent l9 l20)
   (adjacent l20 l10)
   (adjacent l10 l20)
   (adjacent l20 l11)
   (adjacent l11 l20)
   (adjacent l20 l12)
   (adjacent l12 l20)
   (adjacent l20 l13)
   (adjacent l13 l20)
   (adjacent l20 l14)
   (adjacent l14 l20)
   (adjacent l20 l15)
   (adjacent l15 l20)
	(fire-unit-at f1 l14)
	(fire-unit-at f2 l5)
	(fire-unit-at f3 l6)
	(fire-unit-at f4 l3)
	(fire-unit-at f5 l6)
	(fire-unit-at f6 l9)
	(fire-unit-at f7 l5)
	(fire-unit-at f8 l3)
	(fire-unit-at f9 l11)
	(fire-unit-at f10 l14)
	(fire-unit-at f11 l8)
	(fire-unit-at f12 l9)
	(medical-unit-at m1 l2)
	(medical-unit-at m2 l4)
	(medical-unit-at m3 l1)
	(medical-unit-at m4 l10)
	(medical-unit-at m5 l17)
	(medical-unit-at m6 l2)
	(medical-unit-at m7 l16)
	(medical-unit-at m8 l4)
	(medical-unit-at m9 l2)
	(medical-unit-at m10 l18)
	(medical-unit-at m11 l12)
	(medical-unit-at m12 l18)
	(medical-unit-at m13 l10)
	(medical-unit-at m14 l17)
	(medical-unit-at m15 l5)
	(medical-unit-at m16 l16)
	(medical-unit-at m17 l15)
	(medical-unit-at m18 l5)
	(medical-unit-at m19 l12)
	(medical-unit-at m20 l15)
	)
 (:goal (and  (nfire l15) (nfire l10) (nfire l13) (nfire l8) (nfire l18) (nfire l16) (nfire l16) (nfire l4) (nfire l20) (nfire l13) (nfire l18) (nfire l7) (nfire l19) (nfire l3) (nfire l4) (nfire l4) (nfire l18) (nfire l8)  (victim-status v1 healthy) (victim-status v2 healthy) (victim-status v3 healthy) (victim-status v4 healthy) (victim-status v5 healthy) (victim-status v6 healthy) (victim-status v7 healthy) (victim-status v8 healthy) (victim-status v9 healthy) (victim-status v10 healthy) (victim-status v11 healthy) (victim-status v12 healthy) (victim-status v13 healthy) (victim-status v14 healthy) (victim-status v15 healthy) (victim-status v16 healthy) (victim-status v17 healthy) (victim-status v18 healthy)))
 )
