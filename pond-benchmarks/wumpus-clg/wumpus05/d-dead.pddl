
(define (domain wumpus) 

   (:requirements :strips :typing)
   (:types pos )
   (:predicates (adj ?i ?j - pos) (at ?i - pos) (safe ?i - pos) 
                (wumpus-at ?x - pos) (alive) (stench ?i - pos)
                (gold-at ?i - pos) (got-the-treasure)
                (breeze ?i - pos) (pit-at ?p - pos) )
   (:constants
   
    p1-1
    p1-2
    p1-3
    p1-4
    p1-5
    p2-1
    p2-2
    p2-3
    p2-4
    p2-5
    p3-1
    p3-2
    p3-3
    p3-4
    p3-5
    p4-1
    p4-2
    p4-3
    p4-4
    p4-5
    p5-1
    p5-2
    p5-3
    p5-4
    p5-5

     - pos
   )
   
   (:action move
      :parameters (?i - pos ?j - pos )
      :precondition (and (adj ?i ?j) (at ?i) (alive) )
      :effect  (and (not (at ?i)) (at ?j) (when (not (safe ?j)) (not (alive))) )
   )
     
   (:action smell_wumpus
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
      :effect (and (got-the-treasure) (not (gold-at ?i)))
   )
)

