(define (domain forest)
  (:requirements :typing :strips :equality :non-deterministic)
  (:types
     ;;;;;;;top level grid;;;;;;;;
     location 
     problem

     ;;;;;;;subproblem;;;;;;;
     sub-location 
     log-location
     package
     truck
     plane
     city
     block
  )
  (:constants
     ;;;;;;;sub-problem types;;;;;
     grid logistics blocksworld - problem

     ;;;;;;;blocksworld subproblem;;;
     a b c - block

     ;;;;;;;logistics subproblem;;;
     t1 t2 - truck
     a1 - plane
     p1 - package
     l11 l12 l21 l22 - log-location
     c1 c2 - city
  )
  (:predicates 
    ;;grid coordinates
   (at-x ?loc - location)
   (at-y ?loc - location)
   (succ-loc ?loc1 ?loc2 - location)

    ;;subproblem at grid point is solved
   (solved ?locx ?locy - location)

    ;;the subproblem at grid point can be solved
   (enabled ?locx ?locy - location) 
    ;;used to link subproblems 
   (enables ?loc1x ?loc1y ?loc2x ?loc2y  - location) 

   ;;initialize the subproblem at grid point
   (initialized ?locx ?locy - location)
   (ninitialized ?locx ?locy - location)

   ;;subproblem type at each grid point
   (problem-at ?locx ?locy - location ?p - problem)

   ;;;;;grid navigation subproblem;;;;;;;;;;;;;
   (s-at-x ?loc - sub-location)
   (s-at-y ?loc - sub-location)
   (s-succ-loc ?loc1 ?loc2 - sub-location)
   (s-init-x ?loc - sub-location)
   (s-init-y ?loc - sub-location)
   (s-goal-x ?loc - sub-location)
   (s-goal-y ?loc - sub-location)


   ;;;;;logistics subproblem;;;;;;;;;;;;;;;;;;;
   (s-pkg-at ?p - package ?loc - log-location)
   (s-truck-at ?t - truck ?loc - log-location)
   (s-plane-at ?t - plane ?loc - log-location)
   (s-city-loc ?loc - log-location ?c - city)
   (s-airport-loc ?loc - log-location)
   (s-pkg-in-t ?p - package ?t - truck)
   (s-pkg-in-a ?p - package ?a - plane)
   ;;;;;blocksworld subproblem;;;;;;;;;;;;;;;;;
   (s-on ?b1 ?b2 - block)
   (s-on-table ?b - block)
   (s-clear ?b - block)
   (s-empty)
   (s-holding ?b - block)

  )

  ;;;;;top-level grid navigation actions;;;;;;;

  (:action up-x-1
   :parameters (?loc1x ?loc1y ?loc2x ?loc3y - location)
   :precondition (and (succ-loc ?loc1x ?loc2x)
                      (succ-loc ?loc3y ?loc1y)
		      (at-x ?loc1x) (at-y ?loc1y) 
                      (solved ?loc1x ?loc1y))
   :effect (oneof (and (at-x ?loc2x) (not (at-x ?loc1x)))
                  (and (at-y ?loc3y) (not (at-y ?loc1y)))
                  (and))
  )
  (:action up-x-2
   :parameters (?loc1x ?loc1y ?loc2x ?loc2y - location)
   :precondition (and (succ-loc ?loc1x ?loc2x)
                      (succ-loc ?loc1y ?loc2y)
		      (at-x ?loc1x) (at-y ?loc1y) 
                      (solved ?loc1x ?loc1y))
   :effect (oneof (and (at-x ?loc2x) (not (at-x ?loc1x)))
                  (and (at-y ?loc2y) (not (at-y ?loc1y)))
                  (and))
  )

  (:action up-y-1
   :parameters (?loc1x ?loc1y ?loc2y ?loc2x - location)
   :precondition (and (succ-loc ?loc1y ?loc2y)
		      (succ-loc ?loc1x ?loc2x)
		      (at-x ?loc1x) (at-y ?loc1y) 
	  	      (solved ?loc1x ?loc1y))
   :effect (oneof (and (at-y ?loc2y) (not (at-y ?loc1y)))
                  (and (at-x ?loc2x) (not (at-x ?loc1x)))
	          (and))
  )		  

 (:action up-y-2
   :parameters (?loc1x ?loc1y ?loc2y ?loc2x - location)
   :precondition (and (succ-loc ?loc1y ?loc2y)
		      (succ-loc ?loc2x ?loc1x)
		      (at-x ?loc1x) (at-y ?loc1y) 
	  	      (solved ?loc1x ?loc1y))
   :effect (oneof (and (at-y ?loc2y) (not (at-y ?loc1y)))
                  (and (at-x ?loc2x) (not (at-x ?loc1x)))
	          (and))
  )
  (:action down-x-1
   :parameters (?loc1x ?loc1y ?loc2x ?loc2y - location)
   :precondition (and (succ-loc ?loc2x ?loc1x)
                      (succ-loc ?loc2y ?loc1y)
		      (at-x ?loc1x) (at-y ?loc1y) 
                      (solved ?loc1x ?loc1y))
   :effect (oneof (and (at-x ?loc2x) (not (at-x ?loc1x)))
                  (and (at-y ?loc2y) (not (at-y ?loc1y)))
                  (and))
  )
  (:action down-x-2
   :parameters (?loc1x ?loc1y ?loc2x ?loc2y - location)
   :precondition (and (succ-loc ?loc2x ?loc1x)
                      (succ-loc ?loc1y ?loc2y)
		      (at-x ?loc1x) (at-y ?loc1y) 
                      (solved ?loc1x ?loc1y))
   :effect (oneof (and (at-x ?loc2x) (not (at-x ?loc1x)))
                  (and (at-y ?loc2y) (not (at-y ?loc1y)))
                  (and))
  )
  (:action down-y-1
   :parameters (?loc1x ?loc1y ?loc2y ?loc2x - location)
   :precondition (and (succ-loc ?loc2y ?loc1y)
                      (succ-loc ?loc2x ?loc1x)
		      (at-x ?loc1x) (at-y ?loc1y) 
	  	      (solved ?loc1x ?loc1y))
   :effect (oneof (and (at-y ?loc2y) (not (at-y ?loc1y)))
                  (and (at-x ?loc2x) (not (at-x ?loc1x)))
		  (and))
  )

 (:action down-y-2
   :parameters (?loc1x ?loc1y ?loc2y ?loc2x - location)
   :precondition (and (succ-loc ?loc2y ?loc1y)
                      (succ-loc ?loc1x ?loc2x)
		      (at-x ?loc1x) (at-y ?loc1y) 
	  	      (solved ?loc1x ?loc1y))
   :effect (oneof (and (at-y ?loc2y) (not (at-y ?loc1y)))
                  (and (at-x ?loc2x) (not (at-x ?loc1x)))
		  (and))
  )




  ;;;;;sub-problem preparation action;;;;;;;

  (:action make-enabled
   :parameters (?loc1x ?loc1y ?loc2x ?loc2y - location)
   :precondition (and (solved ?loc1x ?loc1y) 
                      (enables ?loc1x ?loc1y ?loc2x ?loc2y)
                 )
   :effect (enabled ?loc2x ?loc2y)
  )





  ;;;;;grid navigation sub-problem;;;;;;;;;;;

  (:action initialize-grid
   :parameters (?slocx ?slocy - sub-location
	        ?locx ?locy - location)
   :precondition (and (at-x ?locx) (at-y ?locy) (enabled ?locx ?locy)
                      (s-init-x ?slocx) (s-init-y ?slocy)
		      (ninitialized ?locx ?locy)
                      (problem-at ?locx ?locy grid)
                 )
   :effect (and (initialized ?locx ?locy) 
                (not (ninitialized ?locx ?locy))
                (s-at-x ?slocx) (s-at-y ?slocy))
  )

  (:action s-up-x
   :parameters (?sloc1x ?sloc1y ?sloc2x - sub-location
                ?locx ?locy - location)
   :precondition (and (initialized ?locx ?locy)
                      (problem-at ?locx ?locy grid)
		      (s-succ-loc ?sloc1x ?sloc2x)
		      (s-at-x ?sloc1x) (s-at-y ?sloc1y))
   :effect (and (s-at-x ?sloc2x) (not (s-at-x ?sloc1x)))
  )

  (:action s-up-y
   :parameters (?sloc1x ?sloc1y ?sloc2y - sub-location
                ?locx ?locy - location)
   :precondition (and (initialized ?locx ?locy)
                      (problem-at ?locx ?locy grid)
		      (s-succ-loc ?sloc1y ?sloc2y)
		      (s-at-x ?sloc1x) (s-at-y ?sloc1y))
   :effect (and (s-at-y ?sloc2y) (not (s-at-y ?sloc1y)))
  )

  (:action s-down-x
   :parameters (?sloc1x ?sloc1y ?sloc2x - sub-location
                ?locx ?locy - location)
   :precondition (and (initialized ?locx ?locy)
                      (problem-at ?locx ?locy grid)
		      (s-succ-loc ?sloc2x ?sloc1x)
		      (s-at-x ?sloc1x) (s-at-y ?sloc1y))
   :effect (and (s-at-x ?sloc2x) (not (s-at-x ?sloc1x)))
  )

  (:action s-down-y
   :parameters (?sloc1x ?sloc1y ?sloc2y - sub-location
                ?locx ?locy - location)
   :precondition (and (initialized ?locx ?locy)
                      (problem-at ?locx ?locy grid)
		      (s-succ-loc ?sloc2y ?sloc1y)
		      (s-at-x ?sloc1x) (s-at-y ?sloc1y))
   :effect (and (s-at-y ?sloc2y) (not (s-at-y ?sloc1y)))
  )

  (:action solve-grid
   :parameters (?slocx ?slocy - sub-location
	        ?locx ?locy - location)
   :precondition (and (at-x ?locx) (at-y ?locy) 
		      (initialized ?locx ?locy)
		      (s-at-x ?slocx) (s-at-y ?slocy)
                      (s-goal-x ?slocx) (s-goal-y ?slocy)
                      (problem-at ?locx ?locy grid)
                 )
   :effect (and (solved ?locx ?locy) 
                (not (s-at-x ?slocx)) (not (s-at-y ?slocy))
           )
  )


  ;;;;;logistics sub-problem;;;;;;;;;;;
  (:action initialize-logistics
   :parameters (?locx ?locy - location)
   :precondition (and (at-x ?locx) (at-y ?locy) (enabled ?locx ?locy)
		      (ninitialized ?locx ?locy)
                      (problem-at ?locx ?locy logistics)
                 )
   :effect (and (initialized ?locx ?locy) 
		(not (ninitialized ?locx ?locy))
		(s-pkg-at p1 l12) (s-truck-at t1 l12)
                (s-truck-at t2 l21) (s-plane-at a1 l11)
           )
  )

  (:action load-truck
   :parameters (?t - truck ?p - package ?loc - log-location)
   :precondition (and (s-truck-at ?t ?loc) (s-pkg-at ?p ?loc))
   :effect (and (s-pkg-in-t ?p ?t) (not (s-pkg-at ?p ?loc)))
  )

  (:action load-plane
   :parameters (?a - plane ?p - package ?loc - log-location)
   :precondition (and (s-plane-at ?a ?loc) (s-pkg-at ?p ?loc))
   :effect (and (s-pkg-in-a ?p ?a) (not (s-pkg-at ?p ?loc)))
  )

  (:action unload-truck
   :parameters (?t - truck ?p - package ?loc - log-location)
   :precondition (and (s-truck-at ?t ?loc) (s-pkg-in-t ?p ?t))
   :effect (and (s-pkg-at ?p ?loc) (not (s-pkg-in-t ?p ?t)))
  )

  (:action unload-plane
   :parameters (?a - plane ?p - package ?loc - log-location)
   :precondition (and (s-plane-at ?a ?loc) (s-pkg-in-a ?p ?a))
   :effect (and (s-pkg-at ?p ?loc) (not (s-pkg-in-a ?p ?a)))
  )

  (:action move-truck
   :parameters (?t - truck ?loc1 ?loc2 - log-location ?c - city)
   :precondition (and (s-truck-at ?t ?loc1) 
                      (s-city-loc ?loc1 ?c)
                      (s-city-loc ?loc2 ?c)
                 )
   :effect (and (not (s-truck-at ?t ?loc1)) (s-truck-at ?t ?loc2))
  ) 

  (:action move-plane
   :parameters (?a - plane ?loc1 ?loc2 - log-location)
   :precondition (and (s-plane-at ?a ?loc1) 
                      (s-airport-loc ?loc1)
                      (s-airport-loc ?loc2)
                 )
   :effect (and (not (s-plane-at ?a ?loc1)) (s-plane-at ?a ?loc2))
  ) 

  (:action solve-logistics
   :parameters (?locx ?locy - location)
   :precondition (and (at-x ?locx) (at-y ?locy) 
		      (initialized ?locx ?locy)
                      (problem-at ?locx ?locy logistics)
                      (s-pkg-at p1 l22)
                 )
   :effect (and (solved ?locx ?locy) 
                (not (s-pkg-at p1 l22))
		(not (s-truck-at t1 l11))
		(not (s-truck-at t1 l12))
		(not (s-truck-at t2 l21))
		(not (s-truck-at t2 l22))
		(not (s-plane-at a1 l11))
		(not (s-plane-at a1 l21))
           )
  )


  ;;;;;blocksworld sub-problem;;;;;;;;;;;
  (:action initialize-blocksworld
   :parameters (?locx ?locy - location)
   :precondition (and (at-x ?locx) (at-y ?locy) (enabled ?locx ?locy)
                      (ninitialized ?locx ?locy)
                      (problem-at ?locx ?locy blocksworld)
                 )
   :effect (and (initialized ?locx ?locy) 
                (not (ninitialized ?locx ?locy))
                (s-on c a) (s-on-table a) (s-on-table b) 
                (s-clear b) (s-clear c) (s-empty)
           )
  )


  (:action stack
   :parameters (?b1 ?b2 - block)
   :precondition (and (s-holding ?b1) (s-clear ?b2))
   :effect (and (s-on ?b1 ?b2) (not (s-holding ?b1)) (not (s-clear ?b2)) (s-clear ?b1) (s-empty))
  )

  (:action putdown
   :parameters (?b1 - block)
   :precondition (and (s-holding ?b1))
   :effect (and (s-on-table ?b1) (not (s-holding ?b1)) (s-clear ?b1) (s-empty))
  )

  (:action unstack
   :parameters (?b1 ?b2 - block)
   :precondition (and (s-empty) (s-clear ?b1) (s-on ?b1 ?b2))
   :effect (and (not (s-on ?b1 ?b2)) (s-holding ?b1) (s-clear ?b2) (not (s-clear ?b1)) (not (s-empty)))
  )

  (:action pickup
   :parameters (?b1 - block)
   :precondition (and (s-empty) (s-clear ?b1))
   :effect (and (not (s-on-table ?b1)) (s-holding ?b1) (not (s-clear ?b1)) (not (s-empty)))
  )

  (:action solve-blocksworld
   :parameters (?locx ?locy - location)
   :precondition (and (at-x ?locx) (at-y ?locy) 
		      (initialized ?locx ?locy)
                      (problem-at ?locx ?locy blocksworld)
                      (s-on a b) (s-on b c)
                 )
   :effect (and (solved ?locx ?locy) 
                (not (s-on a b)) (not (s-on b c))
                (not (s-clear a)) (not (s-empty))
	        (not (s-on-table c))
           )
  )

)


