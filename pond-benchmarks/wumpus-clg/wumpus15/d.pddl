
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
    p1-11
    p1-12
    p1-13
    p1-14
    p1-15
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
    p2-11
    p2-12
    p2-13
    p2-14
    p2-15
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
    p3-11
    p3-12
    p3-13
    p3-14
    p3-15
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
    p4-11
    p4-12
    p4-13
    p4-14
    p4-15
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
    p5-11
    p5-12
    p5-13
    p5-14
    p5-15
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
    p6-11
    p6-12
    p6-13
    p6-14
    p6-15
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
    p7-11
    p7-12
    p7-13
    p7-14
    p7-15
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
    p8-11
    p8-12
    p8-13
    p8-14
    p8-15
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
    p9-11
    p9-12
    p9-13
    p9-14
    p9-15
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
    p10-11
    p10-12
    p10-13
    p10-14
    p10-15
    p11-1
    p11-2
    p11-3
    p11-4
    p11-5
    p11-6
    p11-7
    p11-8
    p11-9
    p11-10
    p11-11
    p11-12
    p11-13
    p11-14
    p11-15
    p12-1
    p12-2
    p12-3
    p12-4
    p12-5
    p12-6
    p12-7
    p12-8
    p12-9
    p12-10
    p12-11
    p12-12
    p12-13
    p12-14
    p12-15
    p13-1
    p13-2
    p13-3
    p13-4
    p13-5
    p13-6
    p13-7
    p13-8
    p13-9
    p13-10
    p13-11
    p13-12
    p13-13
    p13-14
    p13-15
    p14-1
    p14-2
    p14-3
    p14-4
    p14-5
    p14-6
    p14-7
    p14-8
    p14-9
    p14-10
    p14-11
    p14-12
    p14-13
    p14-14
    p14-15
    p15-1
    p15-2
    p15-3
    p15-4
    p15-5
    p15-6
    p15-7
    p15-8
    p15-9
    p15-10
    p15-11
    p15-12
    p15-13
    p15-14
    p15-15

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

