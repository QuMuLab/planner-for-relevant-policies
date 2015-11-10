(define (problem bw_5_10)
    (:domain blocks-domain)
    (:objects
        b1 b2 b3 b4 b5 - block
        l1 l2 l3 l4 l5 - location
    )
    (:init
        (emptyhand)
        (on-table b1)
        (on b2 b3)
        (on-table b3)
        (on b4 b2)
        (on b5 b1)
        (clear b4)
        (clear b5)
        (adjacent l0 l1)
        (adjacent l1 l10)
    )
    (:goal
        (and
            (emptyhand)
            (on-table b1)
            (on-table b2)
            (on-table b3)
            (on-table b4)
            (on-table b5)
            (clear b4)
            (clear b1)
            (clear b2)
            (clear b3)
            (clear b5)
        )
    )
)
