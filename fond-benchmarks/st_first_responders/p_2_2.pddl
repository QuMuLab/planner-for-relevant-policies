(define (problem fr_2_2)
    (:domain first-response)
    (:objects
        l1 l2 - location
        f1 f2 - fire_unit
        v1 v2 - victim
        m1 m2 - medical_unit
    )
    (:init
        (hospital l1)
        (water-at l2)
        (water-at l1)
        (fire l1)
        (victim-at v1 l2)
        (victim-status v1 hurt)
        (victim-at v2 l1)
        (victim-status v2 hurt)
        (adjacent l1 l1)
        (adjacent l2 l2)
        (fire-unit-at f1 l1)
        (fire-unit-at f2 l1)
        (medical-unit-at m1 l2)
        (medical-unit-at m2 l1)
    )
    (:goal
        (and
            (nfire l1)
            (victim-status v1 healthy)
            (victim-status v2 healthy)
        )
    )
)
