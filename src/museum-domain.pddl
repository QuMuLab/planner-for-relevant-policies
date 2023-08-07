(define (domain museum)

(:requirements :non-deterministic)

(:predicates
    (is-agent ?a)(adj ?x ?y)
    
    (is-visitor ?v)
    (at ?x ?y)
    (is-pos ?p)
    
    (needs-restroom ?v)
    (is-fine ?visitor)
    
    
    
    (is-task-history ?t)
    (is-task-p1_1 ?t)
    (is-task-p1_2 ?t)
    (is-task-p1_3 ?t)
    (is-task-p1_4 ?t)
    (is-task-p2_1 ?t)
    (is-task-p2_2 ?t)
    (is-task-p2_3 ?t)
    (is-task-p2_4 ?t)
    
    
    
    (played_P1_1 ?v)
    (played_P1_2 ?v)
    (played_P1_3 ?v)
    (played_P1_4 ?v)
    (played_P2_1 ?v)
    (played_P2_2 ?v)
    (played_P2_3 ?v)
    (played_P2_4 ?v)
    (played_museum_history ?v)
    
)


(:action move
    :parameters (?agent ?from ?to)
    :precondition (and
        (is-agent ?agent)
        (is-pos ?from)
        (is-pos ?to)
        (at ?agent ?from)
        (adj ?from ?to)
    )
    :effect (and
        (not(at ?agent ?from))
        (at ?agent ?to)
    )
)


(:action assist_visitor 
    :parameters (?agent ?visitor ?task )
    :precondition (and
        (is-agent ?agent)
        (is-visitor ?visitor)
        (is-fine ?visitor)
        (is-pos ?task)
        (at ?agent ?task)
    )
    :effect (oneof
        (when (is-task-p1_1 ?task)  (played_P1_1 ?visitor))
        (when (is-task-p1_2 ?task) (played_P1_2 ?visitor))
        (when (is-task-p1_3 ?task) (played_P1_3 ?visitor))
        (when (is-task-p1_4 ?task)  (played_P1_4 ?visitor))
        (when (is-task-p2_1 ?task)  (played_P2_1 ?visitor))
        (when (is-task-p2_2 ?task) (played_P2_2 ?visitor))
        (when (is-task-p2_3 ?task) (played_P2_3 ?visitor))
        (when (is-task-p2_4 ?task)  (played_P2_4 ?visitor))
        (when(is-task-history ?task)  (played_museum_history ?visitor))
    )
)


(:action restroom
    :parameters (?agent ?visitor)
    :precondition (and
        (is-agent ?agent)
        (is-visitor ?visitor)
        (needs-restroom ?visitor)
        
    )
    :effect (is-fine ?visitor)
    
)





)
