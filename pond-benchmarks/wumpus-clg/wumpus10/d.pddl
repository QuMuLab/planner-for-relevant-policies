
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
    p1-6
    p1-7
    p1-8
    p1-9
    p1-10
    p2-1
    p2-2
    p2-3
    p2-4
    p2-5
    p2-6
    p2-7
    p2-8
    p2-9
    p2-10
    p3-1
    p3-2
    p3-3
    p3-4
    p3-5
    p3-6
    p3-7
    p3-8
    p3-9
    p3-10
    p4-1
    p4-2
    p4-3
    p4-4
    p4-5
    p4-6
    p4-7
    p4-8
    p4-9
    p4-10
    p5-1
    p5-2
    p5-3
    p5-4
    p5-5
    p5-6
    p5-7
    p5-8
    p5-9
    p5-10
    p6-1
    p6-2
    p6-3
    p6-4
    p6-5
    p6-6
    p6-7
    p6-8
    p6-9
    p6-10
    p7-1
    p7-2
    p7-3
    p7-4
    p7-5
    p7-6
    p7-7
    p7-8
    p7-9
    p7-10
    p8-1
    p8-2
    p8-3
    p8-4
    p8-5
    p8-6
    p8-7
    p8-8
    p8-9
    p8-10
    p9-1
    p9-2
    p9-3
    p9-4
    p9-5
    p9-6
    p9-7
    p9-8
    p9-9
    p9-10
    p10-1
    p10-2
    p10-3
    p10-4
    p10-5
    p10-6
    p10-7
    p10-8
    p10-9
    p10-10

     - pos
   )
   
   (:action move
      :parameters (?i - pos ?j - pos )
      :precondition (and (adj ?i ?j) (at ?i) (alive) (safe ?j) )
      :effect  (and (not (at ?i)) (at ?j))
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

