
(define (domain wumpus-contingent) 

   (:requirements :strips :typing)
   (:types pos )
   (:predicates (adj ?i ?j - pos) (at ?i - pos) (safe ?i - pos) 
                (wumpus-at ?x - pos) (alive) (stench ?i - pos) (gold-at ?i - pos) (got-the-treasure)
                (breeze ?i - pos) (pit-at ?p - pos) )
 (:constants

    p1-1
    p1-2
    p1-3
    p1-4
    p1-5
    p1-6
    p1-7
    p2-1
    p2-2
    p2-3
    p2-4
    p2-5
    p2-6
    p2-7
    p3-1
    p3-2
    p3-3
    p3-4
    p3-5
    p3-6
    p3-7
    p4-1
    p4-2
    p4-3
    p4-4
    p4-5
    p4-6
    p4-7
    p5-1
    p5-2
    p5-3
    p5-4
    p5-5
    p5-6
    p5-7
    p6-1
    p6-2
    p6-3
    p6-4
    p6-5
    p6-6
    p6-7
    p7-1
    p7-2
    p7-3
    p7-4
    p7-5
    p7-6
    p7-7

 - pos  )
               
   (:action smell-wumpus
     :parameters (?pos - pos )
     :precondition (and (alive) (at ?pos) )
     :observe (stench ?pos)
)



(:action feel-breeze
     :parameters (?pos - pos )
     :precondition (and (alive) (at ?pos) )
     :observe (breeze ?pos)
)
 
 
   (:action grab
      :parameters ( ?i - pos)
      :precondition (and (at ?i) (gold-at ?i) (alive))
      :effect (and (got-the-treasure) (not (gold-at ?i))))

;   (:action move ;ideal
;      :parameters (?i - pos ?j - pos )
;      :precondition (and (adj ?i ?j) (at ?i) (alive) )
;      :effect (and  	
;	    	(not (at ?i)) (at ?j)
;                (when (and (wumpus-at ?j) (not (wumpus-killed))) (not (alive)) )
;   ))

   (:action move
      :parameters (?i - pos ?j - pos )
      :precondition (and (adj ?i ?j) (at ?i) (alive) )
      :effect  (and (not (at ?i)) (at ?j) (when (not (safe ?j)) (not (alive))) )
    )


)

