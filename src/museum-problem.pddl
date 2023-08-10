;in this case, the task is the first painting and the visitor needs the restroom


(define (problem museum-problem) (:domain museum)
(:objects 
    agent ; agent pepper element
    vis1 ; visitor element
    task ;a task element
    p0 ;initial position
    p11 ; positions of room1
    p21
    p31
    p41
    p12 ;positions of room2
    p22
    p32
    p42 
)

(:init
    (is-agent agent) 
    (is-visitor vis1) 
    (is-pos p0) ;p0 the starting position of pepper is assumed neutral (between room1 and room2)
    (is-pos p11)(is-pos p21)(is-pos p31)(is-pos p41) ;positions of room1
    (is-pos p12)(is-pos p22)(is-pos p32)(is-pos p42) ;positions of room2
    (is-pos task)
    (at agent p0)
    
    ;--------- new

    (adj p0 p11)(adj p11 p0) ; adjacencies of the paintings (placed at the 4 walls of a room) STANZA 1
    (adj p11 p21)(adj p21 p11)
    (adj p21 p31)(adj p31 p21)
    (adj p31 p41)(adj p41 p31)
    (adj p41 p0)(adj p0 p41)

    (adj p0 p12)(adj p12 p0) ; adjacencies of the paintings (placed at the 4 walls of a room) STANZA 2
    (adj p12 p22)(adj p22 p12)
    (adj p22 p32)(adj p32 p22)
    (adj p32 p42)(adj p42 p32)
    (adj p42 p0)(adj p0 p42)

    ;---------

    
    ;(adj p0 task) todo: definire bene adiacenze OLD


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
