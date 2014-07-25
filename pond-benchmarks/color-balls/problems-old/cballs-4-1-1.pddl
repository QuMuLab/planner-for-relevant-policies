(define (problem n4-b1-c1)
    (:domain colored-balls)
    (:objects
        p1 p2 p3 p4 - pos
        b1 - ball
        c1 - color)
    (:init
        (suc p1 p2) (suc p2 p3) (suc p3 p4)
        (at p1 p1)
        (empty-arm)
        (spot p3 p1 c1)
        (not (ball-at-spot b1))
        (oneof (ball-color b1 c1))
        (oneof (ball-at-spot b1)
                   (ball-pos b1 p1 p1) (ball-pos b1 p1 p2) (ball-pos b1 p1 p3) (ball-pos b1 p1 p4)
                   (ball-pos b1 p2 p1) (ball-pos b1 p2 p2) (ball-pos b1 p2 p3) (ball-pos b1 p2 p4)
                   (ball-pos b1 p3 p1) (ball-pos b1 p3 p2) (ball-pos b1 p3 p3) (ball-pos b1 p3 p4)
                   (ball-pos b1 p4 p1) (ball-pos b1 p4 p2) (ball-pos b1 p4 p3) (ball-pos b1 p4 p4))
    )
    (:goal (and (ball-at-spot b1)))
)
