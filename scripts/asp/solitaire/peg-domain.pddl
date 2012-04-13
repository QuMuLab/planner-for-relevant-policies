;; Peg Solitaire sequential domain

(define (domain pegsolitaire-sequential)
    (:requirements :typing :action-costs)
    (:types location time-step - object)
    (:predicates
        (IN-LINE ?x ?y ?z - location)
        (occupied ?l - location)
        (free ?l - location)
        (at-time ?t - time-step)
        (consecutive ?t1 - time-step ?t2 - time-step)
    )
    
    (:functions (total-cost) - number)

    (:action move
     :parameters (?from - location ?over - location ?to - location ?t1 - time-step ?t2 - time-step)
     :precondition (and 
                       (IN-LINE ?from ?over ?to)
                       (occupied ?from)
                       (occupied ?over)
                       (free ?to)
                       (at-time ?t1)
                       (consecutive ?t1 ?t2)
                   )
     :effect (and
                 (not (occupied ?from))
                 (not (occupied ?over))
                 (not (free ?to))
                 (free ?from)
                 (free ?over)
                 (occupied ?to)
                 (not (at-time ?t1))
                 (at-time ?t2)
                 (increase (total-cost) 1)
             )
    )
)
