(define (domain colored-balls)
    (:requirements :typing :equality)
    (:types pos ball color)
    (:predicates
        (suc ?x ?y - pos)
        (ball-pos ?b - ball ?x ?y - pos)
        (holding ?b - ball)
        (empty-arm)
        (ball-color ?b - ball ?c - color)
        (spot ?x ?y - pos ?c - color)
        (ball-at-spot ?b - ball)
        (at ?x ?y - pos)
    )

    (:action up
        :parameters (?x ?y1 ?y2 - pos)
        :precondition (and (at ?x ?y1) (suc ?y1 ?y2))
        :effect (and (not (at ?x ?y1)) (at ?x ?y2))
    )
    (:action down
        :parameters (?x ?y1 ?y2 - pos)
        :precondition (and (at ?x ?y1) (suc ?y2 ?y1))
        :effect (and (not (at ?x ?y1)) (at ?x ?y2))
    )
    (:action right
        :parameters (?x1 ?x2 ?y - pos)
        :precondition (and (at ?x1 ?y) (suc ?x1 ?x2))
        :effect (and (not (at ?x1 ?y)) (at ?x2 ?y))
    )
    (:action left
        :parameters (?x1 ?x2 ?y - pos)
        :precondition (and (at ?x1 ?y) (suc ?x2 ?x1))
        :effect (and (not (at ?x1 ?y)) (at ?x2 ?y))
    )
    (:action pick-up
        :parameters (?b - ball ?x ?y - pos)
        :precondition (and (at ?x ?y) (ball-pos ?b ?x ?y) (empty-arm))
        :effect (and (not (ball-pos ?b ?x ?y)) (not (empty-arm)) (holding ?b))
    )
    (:action drop-ball-at-spot
        :parameters (?b - ball ?c - color ?x ?y - pos)
        :precondition (and (at ?x ?y) (holding ?b) (ball-color ?b ?c) (spot ?x ?y ?c))
        :effect (and (not (holding ?b)) (ball-at-spot ?b) (empty-arm))
    )

    (:action obs-ball-pos
        :parameters (?b - ball ?x ?y - pos)
        :precondition (and (at ?x ?y))
        :observe (ball-pos ?b ?x ?y)
    )
    (:action obs-ball-color
        :parameters (?b - ball ?c - color ?x ?y - pos)
        :precondition (and (at ?x ?y) (ball-pos ?b ?x ?y))
        :observe (ball-color ?b ?c)
    )
)

