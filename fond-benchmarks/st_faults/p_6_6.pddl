(define (problem fault_o6_f6)
    (:domain faults)
    (:init
        (not_completed o1)
        (not_completed o2)
        (not_completed o3)
        (not_completed o4)
        (not_completed o5)
        (not_completed o6)
        (not_fault f1)
        (not_fault f2)
        (not_fault f3)
        (not_fault f4)
        (not_fault f5)
        (not_fault f6)
    )
    (:goal
        (made)
    )
)
