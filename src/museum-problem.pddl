;in this case, the task is the first painting and the visitor needs the restroom


(define (problem museum-problem) (:domain museum)
(:objects 
    agent ; agent pepper element
    vis1 ; visitor element
    task ;a task element
    p0 ;initial position
)

(:init
    (is-agent agent) 
    (is-visitor vis1) 
    (is-pos p0)
    (is-pos task)
    (at agent p0)
    (adj p0 task) ;todo: definire bene adiacenze


    ;da aggiornare dinamicamente
    (is-task-p1_1 task)
    (needs-restroom vis1)
    ;------------------
)


; in the goal must be specified where the final agent's position, the paintings to NOT play
; and the painting to play
(:goal (and
    ;da aggiornare dinamicamente
    (played_P1_1 vis1)
    ;---------------
))

)

; in this file the starting position of pepper is supposed to be pos0 between the paintings 1 and 4, 
; which are placed at the 4 walls of a room
