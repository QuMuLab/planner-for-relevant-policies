(define (problem fr_1_8)
    (:domain first-response)
    (:objects
        l1 - location
        f1 - fire_unit
        v1 v2 v3 v4 v5 v6 v7 v8 - victim
        m1 - medical_unit
    )
    (:init
        (hospital l1)
        (water-at l1)
        (fire l1)
        (victim-at v1 l1)
        (victim-status v1 hurt)
        (victim-at v2 l1)
        (victim-status v2 hurt)
        (victim-at v3 l1)
        (victim-status v3 dying)
        (victim-at v4 l1)
        (victim-status v4 dying)
        (victim-at v5 l1)
        (victim-status v5 hurt)
        (victim-at v6 l1)
        (victim-status v6 hurt)
        (victim-at v7 l1)
        (victim-status v7 dying)
        (victim-at v8 l1)
        (victim-status v8 dying)
        (adjacent l1 l1)
        (fire-unit-at f1 l1)
        (medical-unit-at m1 l1)
    )
    (:goal
        (and
            (nfire l1)
            (victim-status v1 healthy)
            (victim-status v2 healthy)
            (victim-status v3 healthy)
            (victim-status v4 healthy)
            (victim-status v5 healthy)
            (victim-status v6 healthy)
            (victim-status v7 healthy)
            (victim-status v8 healthy)
        )
    )
)
