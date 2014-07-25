(define (domain doors)
    (:requirements :typing :equality)
    (:types pos)
    (:predicates
        (suc ?x ?y - pos)
        (wall ?x ?y - pos)
        (door ?x ?y - pos)
        (at ?x ?y - pos)
    )

    (:action up
        :parameters (?x ?y1 ?y2 - pos)
        :precondition (and (at ?x ?y1) (suc ?y1 ?y2) (not (wall ?x ?y2)))
        :effect (and (not (at ?x ?y1)) (at ?x ?y2))
    )
    (:action down
        :parameters (?x ?y1 ?y2 - pos)
        :precondition (and (at ?x ?y1) (suc ?y2 ?y1) (not (wall ?x ?y2)))
        :effect (and (not (at ?x ?y1)) (at ?x ?y2))
    )
    (:action step-into-door
        :parameters (?x1 ?x2 ?y - pos)
        :precondition (and (at ?x1 ?y) (suc ?x1 ?x2) (door ?x2 ?y))
        :effect (and (not (at ?x1 ?y)) (at ?x2 ?y))
    )
    (:action step-outof-door
        :parameters (?x1 ?x2 ?y - pos)
        :precondition (and (at ?x1 ?y) (suc ?x1 ?x2) (door ?x1 ?y))
        :effect (and (not (at ?x1 ?y)) (at ?x2 ?y))
    )

    (:action door-obs
      :parameters (?x1 ?x2 ?y - pos)
      :precondition (and (at ?x1 ?y) (suc ?x1 ?x2))
      :observe (door ?x2 ?y)
    )
)

