(define (problem fr_7_5)
    (:domain first-response)
    (:objects
        l1 l2 l3 l4 l5 l6 l7 - location
        f1 f2 f3 f4 - fire_unit
        v1 v2 v3 v4 v5 - victim
        m1 m2 m3 m4 m5 m6 m7 - medical_unit
    )
    (:init
        (hospital l6)
        (hospital l5)
        (hospital l3)
        (water-at l4)
        (water-at l3)
        (fire l1)
        (victim-at v1 l7)
        (victim-status v1 hurt)
        (victim-at v2 l7)
        (victim-status v2 dying)
        (victim-at v3 l7)
        (victim-status v3 dying)
        (victim-at v4 l7)
        (victim-status v4 hurt)
        (victim-at v5 l7)
        (victim-status v5 hurt)
        (adjacent l1 l1)
        (adjacent l2 l2)
        (adjacent l3 l3)
        (adjacent l4 l4)
        (adjacent l5 l5)
        (adjacent l6 l6)
        (adjacent l7 l7)
        (adjacent l2 l1)
        (adjacent l1 l2)
        (adjacent l2 l3)
        (adjacent l3 l2)
        (adjacent l3 l1)
        (adjacent l1 l3)
        (adjacent l3 l4)
        (adjacent l4 l3)
        (adjacent l3 l5)
        (adjacent l5 l3)
        (adjacent l3 l6)
        (adjacent l6 l3)
        (adjacent l4 l1)
        (adjacent l1 l4)
        (adjacent l4 l2)
        (adjacent l2 l4)
        (adjacent l5 l1)
        (adjacent l1 l5)
        (adjacent l5 l2)
        (adjacent l2 l5)
        (adjacent l5 l4)
        (adjacent l4 l5)
        (adjacent l6 l1)
        (adjacent l1 l6)
        (adjacent l7 l1)
        (adjacent l1 l7)
        (adjacent l7 l2)
        (adjacent l2 l7)
        (adjacent l7 l3)
        (adjacent l3 l7)
        (fire-unit-at f1 l7)
        (fire-unit-at f2 l6)
        (fire-unit-at f3 l4)
        (fire-unit-at f4 l3)
        (medical-unit-at m1 l1)
        (medical-unit-at m2 l6)
        (medical-unit-at m3 l5)
        (medical-unit-at m4 l3)
        (medical-unit-at m5 l2)
        (medical-unit-at m6 l1)
        (medical-unit-at m7 l6)
    )
    (:goal
        (and
            (nfire l1)
            (victim-status v1 healthy)
            (victim-status v2 healthy)
            (victim-status v3 healthy)
            (victim-status v4 healthy)
            (victim-status v5 healthy)
        )
    )
)
