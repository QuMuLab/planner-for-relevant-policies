(define (problem wumpus-contingent-7-4-1)
(:domain wumpus-contingent)


   (:init
    (and
     (at p1-1)
     (alive)

     (adj p1-2 p2-2)
     (adj p2-2 p1-2)

     (adj p1-3 p2-3)
     (adj p2-3 p1-3)

     (adj p1-4 p2-4)
     (adj p2-4 p1-4)

     (adj p1-5 p2-5)
     (adj p2-5 p1-5)

     (adj p1-6 p2-6)
     (adj p2-6 p1-6)

     (adj p1-7 p2-7)
     (adj p2-7 p1-7)

     (adj p2-1 p3-1)
     (adj p3-1 p2-1)

     (adj p2-2 p3-2)
     (adj p3-2 p2-2)

     (adj p2-3 p3-3)
     (adj p3-3 p2-3)

     (adj p2-4 p3-4)
     (adj p3-4 p2-4)

     (adj p2-5 p3-5)
     (adj p3-5 p2-5)

     (adj p2-6 p3-6)
     (adj p3-6 p2-6)

     (adj p2-7 p3-7)
     (adj p3-7 p2-7)

     (adj p3-1 p4-1)
     (adj p4-1 p3-1)

     (adj p3-2 p4-2)
     (adj p4-2 p3-2)

     (adj p3-3 p4-3)
     (adj p4-3 p3-3)

     (adj p3-4 p4-4)
     (adj p4-4 p3-4)

     (adj p3-5 p4-5)
     (adj p4-5 p3-5)

     (adj p3-6 p4-6)
     (adj p4-6 p3-6)

     (adj p3-7 p4-7)
     (adj p4-7 p3-7)

     (adj p4-1 p5-1)
     (adj p5-1 p4-1)

     (adj p4-2 p5-2)
     (adj p5-2 p4-2)

     (adj p4-3 p5-3)
     (adj p5-3 p4-3)

     (adj p4-4 p5-4)
     (adj p5-4 p4-4)

     (adj p4-5 p5-5)
     (adj p5-5 p4-5)

     (adj p4-6 p5-6)
     (adj p5-6 p4-6)

     (adj p4-7 p5-7)
     (adj p5-7 p4-7)

     (adj p5-1 p6-1)
     (adj p6-1 p5-1)

     (adj p5-2 p6-2)
     (adj p6-2 p5-2)

     (adj p5-3 p6-3)
     (adj p6-3 p5-3)

     (adj p5-4 p6-4)
     (adj p6-4 p5-4)

     (adj p5-5 p6-5)
     (adj p6-5 p5-5)

     (adj p5-6 p6-6)
     (adj p6-6 p5-6)

     (adj p5-7 p6-7)
     (adj p6-7 p5-7)

     (adj p6-1 p7-1)
     (adj p7-1 p6-1)

     (adj p6-2 p7-2)
     (adj p7-2 p6-2)

     (adj p6-3 p7-3)
     (adj p7-3 p6-3)

     (adj p6-4 p7-4)
     (adj p7-4 p6-4)

     (adj p6-5 p7-5)
     (adj p7-5 p6-5)

     (adj p6-6 p7-6)
     (adj p7-6 p6-6)

     (adj p6-7 p7-7)
     (adj p7-7 p6-7)


     (adj p1-1 p1-2)
     (adj p1-2 p1-1)

     (adj p2-1 p2-2)
     (adj p2-2 p2-1)

     (adj p3-1 p3-2)
     (adj p3-2 p3-1)

     (adj p4-1 p4-2)
     (adj p4-2 p4-1)

     (adj p5-1 p5-2)
     (adj p5-2 p5-1)

     (adj p6-1 p6-2)
     (adj p6-2 p6-1)

     (adj p7-1 p7-2)
     (adj p7-2 p7-1)

     (adj p1-2 p1-3)
     (adj p1-3 p1-2)

     (adj p2-2 p2-3)
     (adj p2-3 p2-2)

     (adj p3-2 p3-3)
     (adj p3-3 p3-2)

     (adj p4-2 p4-3)
     (adj p4-3 p4-2)

     (adj p5-2 p5-3)
     (adj p5-3 p5-2)

     (adj p6-2 p6-3)
     (adj p6-3 p6-2)

     (adj p7-2 p7-3)
     (adj p7-3 p7-2)

     (adj p1-3 p1-4)
     (adj p1-4 p1-3)

     (adj p2-3 p2-4)
     (adj p2-4 p2-3)

     (adj p3-3 p3-4)
     (adj p3-4 p3-3)

     (adj p4-3 p4-4)
     (adj p4-4 p4-3)

     (adj p5-3 p5-4)
     (adj p5-4 p5-3)

     (adj p6-3 p6-4)
     (adj p6-4 p6-3)

     (adj p7-3 p7-4)
     (adj p7-4 p7-3)

     (adj p1-4 p1-5)
     (adj p1-5 p1-4)

     (adj p2-4 p2-5)
     (adj p2-5 p2-4)

     (adj p3-4 p3-5)
     (adj p3-5 p3-4)

     (adj p4-4 p4-5)
     (adj p4-5 p4-4)

     (adj p5-4 p5-5)
     (adj p5-5 p5-4)

     (adj p6-4 p6-5)
     (adj p6-5 p6-4)

     (adj p7-4 p7-5)
     (adj p7-5 p7-4)

     (adj p1-5 p1-6)
     (adj p1-6 p1-5)

     (adj p2-5 p2-6)
     (adj p2-6 p2-5)

     (adj p3-5 p3-6)
     (adj p3-6 p3-5)

     (adj p4-5 p4-6)
     (adj p4-6 p4-5)

     (adj p5-5 p5-6)
     (adj p5-6 p5-5)

     (adj p6-5 p6-6)
     (adj p6-6 p6-5)

     (adj p7-5 p7-6)
     (adj p7-6 p7-5)

     (adj p1-6 p1-7)
     (adj p1-7 p1-6)

     (adj p2-6 p2-7)
     (adj p2-7 p2-6)

     (adj p3-6 p3-7)
     (adj p3-7 p3-6)

     (adj p4-6 p4-7)
     (adj p4-7 p4-6)

     (adj p5-6 p5-7)
     (adj p5-7 p5-6)

     (adj p6-6 p6-7)
     (adj p6-7 p6-6)

     (adj p7-6 p7-7)
     (adj p7-7 p7-6)

 
     (gold-at p7-7)

        (safe p1-1)
        (safe p1-2)
        (safe p1-3)
        (safe p1-4)
        (safe p1-5)
        (safe p1-6)
        (safe p1-7)
  
        (safe p2-1)
        (safe p2-2)

        (safe p2-4)
        (safe p2-5)
        (safe p2-6)
        (safe p2-7)
  
        (safe p3-1)
        (safe p3-3)
        (safe p3-5)
        (safe p3-6)
        (safe p3-7)
  
        (safe p4-1)
        (safe p4-2)
        (safe p4-4)
        (safe p4-6)
        (safe p4-7)
  
        (safe p5-1)
        (safe p5-2)
        (safe p5-3)
        (safe p5-5)
        (safe p5-7)
  
        (safe p6-1)
        (safe p6-2)
        (safe p6-3)
        (safe p6-4)
        (safe p6-6)
  
        (safe p7-1)
        (safe p7-2)
        (safe p7-3)
        (safe p7-4)
        (safe p7-5)
        (safe p7-7)
 


(oneof
   (safe p2-3)
   (safe p3-2)
)

(oneof
 (safe p3-4)
 (safe p4-3)
)

(oneof
(safe p5-4)
(safe p4-5)
)

(oneof
 (safe p6-5)
 (safe p5-6)
)

(oneof
(safe p6-7)
(safe p7-6)
)


(or (not (safe p2-3)) (not (wumpus-at p2-3)) )
(or (not (safe p2-3)) (not (pit-at p2-3)) )
(or (safe p2-3) (wumpus-at p2-3) (pit-at p2-3) )

(or (not (safe p3-2)) (not (wumpus-at p3-2)) )
(or (not (safe p3-2)) (not (pit-at p3-2)) )
(or (safe p3-2) (wumpus-at p3-2)(pit-at p3-2) )

(or (not (safe p3-4)) (not (wumpus-at p3-4)) )
(or (not (safe p3-4)) (not (pit-at p3-4)) )
(or (safe p3-4) (wumpus-at p3-4)(pit-at p3-4) )

(or (not (safe p4-3)) (not (wumpus-at p4-3)) )
(or (not (safe p4-3)) (not (pit-at p4-3)) )
(or (safe p4-3) (wumpus-at p4-3)(pit-at p4-3) )

(or (not (safe p5-4)) (not (wumpus-at p5-4)) )
(or (not (safe p5-4)) (not (pit-at p5-4)) )
(or (safe p5-4) (wumpus-at p5-4)(pit-at p5-4) )

(or (not (safe p4-5)) (not (wumpus-at p4-5)) )
(or (not (safe p4-5)) (not (pit-at p4-5)) )
(or (safe p4-5) (wumpus-at p4-5)(pit-at p4-5) )

(or (not (safe p6-5)) (not (wumpus-at p6-5)) )
(or (not (safe p6-5)) (not (pit-at p6-5)) )
(or (safe p6-5) (wumpus-at p6-5)(pit-at p6-5) )

(or (not (safe p5-6)) (not (wumpus-at p5-6)) )
(or (not (safe p5-6)) (not (pit-at p5-6)) )
(or (safe p5-6) (wumpus-at p5-6)(pit-at p5-6) )

(or (not (safe p6-7)) (not (wumpus-at p6-7)) )
(or (not (safe p6-7)) (not (pit-at p6-7)) )
(or (safe p6-7) (wumpus-at p6-7)(pit-at p6-7) )

(or (not (safe p7-6)) (not (wumpus-at p7-6)) )
(or (not (safe p7-6)) (not (pit-at p7-6)) )
(or (safe p7-6) (wumpus-at p7-6)(pit-at p7-6) )


;; wumpuses
(or (stench p1-3) (not (wumpus-at p2-3)))
(or (not (stench p1-3))  (wumpus-at p2-3))

(or (stench p3-1) (not (wumpus-at p3-2)))
(or (not (stench p3-1))  (wumpus-at p3-2))

(or (not (stench p2-2)) (wumpus-at p3-2) (wumpus-at p2-3))
(or (stench p2-2) (not (wumpus-at p3-2)))
(or (stench p2-2) (not (wumpus-at p2-3)))

(or (not (stench p3-3)) (wumpus-at p3-2) (wumpus-at p2-3)(wumpus-at p3-4) (wumpus-at p4-3) )
(or (stench p3-3) (not (wumpus-at p3-2)))
(or (stench p3-3) (not (wumpus-at p2-3)))
(or (stench p3-3) (not (wumpus-at p3-4)))
(or (stench p3-3) (not (wumpus-at p4-3)))

(or (not (stench p2-4)) (wumpus-at p2-3)(wumpus-at p3-4) )
(or (stench p2-4) (not (wumpus-at p2-3)))
(or (stench p2-4) (not (wumpus-at p3-4)))

(or (not (stench p4-2)) (wumpus-at p4-3)(wumpus-at p3-2) )
(or (stench p4-2) (not (wumpus-at p4-3)))
(or (stench p4-2) (not (wumpus-at p3-2)))

(or (not (stench p4-4)) (wumpus-at p4-5) (wumpus-at p5-4)(wumpus-at p3-4) (wumpus-at p4-3) )
(or (stench p4-4) (not (wumpus-at p4-5)))
(or (stench p4-4) (not (wumpus-at p5-4)))
(or (stench p4-4) (not (wumpus-at p3-4)))
(or (stench p4-4) (not (wumpus-at p4-3)))

(or (not (stench p3-5)) (wumpus-at p4-5)(wumpus-at p3-4) )
(or (stench p3-5) (not (wumpus-at p4-5)))
(or (stench p3-5) (not (wumpus-at p3-4)))

(or (not (stench p5-3)) (wumpus-at p4-3)(wumpus-at p5-4) )
(or (stench p5-3) (not (wumpus-at p4-3)))
(or (stench p5-3) (not (wumpus-at p5-4)))


(or (not (stench p5-5)) (wumpus-at p4-5) (wumpus-at p5-4)(wumpus-at p5-6) (wumpus-at p6-5) )
(or (stench p5-5) (not (wumpus-at p4-5)))
(or (stench p5-5) (not (wumpus-at p5-4)))
(or (stench p5-5) (not (wumpus-at p6-5)))
(or (stench p5-5) (not (wumpus-at p5-6)))

(or (not (stench p4-6)) (wumpus-at p5-6)(wumpus-at p4-5) )
(or (stench p4-6) (not (wumpus-at p5-6)))
(or (stench p4-6) (not (wumpus-at p4-5)))

(or (not (stench p6-4)) (wumpus-at p6-5)(wumpus-at p5-4) )
(or (stench p6-4) (not (wumpus-at p5-4)))
(or (stench p6-4) (not (wumpus-at p6-5)))

(or (not (stench p6-6)) (wumpus-at p5-6) (wumpus-at p6-5)(wumpus-at p6-7) (wumpus-at p7-6) )
(or (stench p6-6) (not (wumpus-at p5-6)))
(or (stench p6-6) (not (wumpus-at p6-5)))
(or (stench p6-6) (not (wumpus-at p6-7)))
(or (stench p6-6) (not (wumpus-at p7-6)))

(or (not (stench p5-7)) (wumpus-at p5-6)(wumpus-at p6-7) )
(or (stench p5-7) (not (wumpus-at p5-6)))
(or (stench p5-7) (not (wumpus-at p6-7)))

(or (not (stench p7-5)) (wumpus-at p7-6)(wumpus-at p6-5) )
(or (stench p7-5) (not (wumpus-at p6-5)))
(or (stench p7-5) (not (wumpus-at p7-6)))

(or (not (stench p7-7)) (wumpus-at p6-7)(wumpus-at p7-6) )
(or (stench p7-7) (not (wumpus-at p6-7)))
(or (stench p7-7) (not (wumpus-at p7-6)))


;; pits
(or (breeze p1-3) (not (pit-at p2-3)))
(or (not (breeze p1-3))  (pit-at p2-3))

(or (breeze p3-1) (not (pit-at p3-2)))
(or (not (breeze p3-1))  (pit-at p3-2))

(or (not (breeze p2-2)) (pit-at p3-2) (pit-at p2-3))
(or (breeze p2-2) (not (pit-at p3-2)))
(or (breeze p2-2) (not (pit-at p2-3)))

(or (not (breeze p3-3)) (pit-at p3-2) (pit-at p2-3))
(or (breeze p3-3) (not (pit-at p3-2)))
(or (breeze p3-3) (not (pit-at p2-3)))

(or (not (breeze p3-3)) (pit-at p3-2) (pit-at p2-3)(pit-at p3-4) (pit-at p4-3) )
(or (breeze p3-3) (not (pit-at p3-2)))
(or (breeze p3-3) (not (pit-at p2-3)))
(or (breeze p3-3) (not (pit-at p3-4)))
(or (breeze p3-3) (not (pit-at p4-3)))

(or (not (breeze p2-4)) (pit-at p2-3)(pit-at p3-4) )
(or (breeze p2-4) (not (pit-at p2-3)))
(or (breeze p2-4) (not (pit-at p3-4)))

(or (not (breeze p4-2)) (pit-at p4-3)(pit-at p3-2) )
(or (breeze p4-2) (not (pit-at p4-3)))
(or (breeze p4-2) (not (pit-at p3-2)))

(or (not (breeze p4-4)) (pit-at p4-5) (pit-at p5-4)(pit-at p3-4) (pit-at p4-3) )
(or (breeze p4-4) (not (pit-at p4-5)))
(or (breeze p4-4) (not (pit-at p5-4)))
(or (breeze p4-4) (not (pit-at p3-4)))
(or (breeze p4-4) (not (pit-at p4-3)))

(or (not (breeze p3-5)) (pit-at p4-5)(pit-at p3-4) )
(or (breeze p3-5) (not (pit-at p4-5)))
(or (breeze p3-5) (not (pit-at p3-4)))

(or (not (breeze p5-3)) (pit-at p4-3)(pit-at p5-4) )
(or (breeze p5-3) (not (pit-at p4-3)))
(or (breeze p5-3) (not (pit-at p5-4)))

(or (not (breeze p5-5)) (pit-at p4-5) (pit-at p5-4)(pit-at p5-6) (pit-at p6-5) )
(or (breeze p5-5) (not (pit-at p4-5)))
(or (breeze p5-5) (not (pit-at p5-4)))
(or (breeze p5-5) (not (pit-at p6-5)))
(or (breeze p5-5) (not (pit-at p5-6)))

(or (not (breeze p4-6)) (pit-at p5-6)(pit-at p4-5) )
(or (breeze p4-6) (not (pit-at p5-6)))
(or (breeze p4-6) (not (pit-at p4-5)))

(or (not (breeze p6-4)) (pit-at p6-5)(pit-at p5-4) )
(or (breeze p6-4) (not (pit-at p5-4)))
(or (breeze p6-4) (not (pit-at p6-5)))

(or (not (breeze p6-6)) (pit-at p5-6) (pit-at p6-5)(pit-at p6-7) (pit-at p7-6) )
(or (breeze p6-6) (not (pit-at p5-6)))
(or (breeze p6-6) (not (pit-at p6-5)))
(or (breeze p6-6) (not (pit-at p6-7)))
(or (breeze p6-6) (not (pit-at p7-6)))

(or (not (breeze p5-7)) (pit-at p5-6)(pit-at p6-7) )
(or (breeze p5-7) (not (pit-at p5-6)))
(or (breeze p5-7) (not (pit-at p6-7)))

(or (not (breeze p7-5)) (pit-at p7-6)(pit-at p6-5) )
(or (breeze p7-5) (not (pit-at p6-5)))
(or (breeze p7-5) (not (pit-at p7-6)))

(or (not (breeze p7-7)) (pit-at p6-7)(pit-at p7-6) )
(or (breeze p7-7) (not (pit-at p6-7)))
(or (breeze p7-7) (not (pit-at p7-6)))

  )
 )
      (:goal (and (got-the-treasure) (alive)) ) 
)
