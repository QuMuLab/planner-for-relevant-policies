(define (problem p1)
 (:domain forest)
 (:objects
           x1 y1  - location
		 sx1 sy1  - sub-location
 )
 (:init 
	;;;;;;;;top level grid;;;;;;;
	(at-x x1) 
	(at-y y1)
	(ninitialized x1 y1)
	;;;;;;;;subproblems;;;;;;;;;;
  (problem-at x1 y1 blocksworld)
        ;;;;;;;;enabling constraints;;
	(enabled x1 y1)
	(solved x1 y1)
	;;;;;;;;grid sub-problem;;;;;;
	(s-init-x sx1)
	(s-init-y sy1)
	(s-goal-x sx1)
	(s-goal-y sy1)
	;;;;;;logistics sub-problem;;
                (s-city-loc l11 c1) (s-city-loc l12 c1)
                (s-city-loc l21 c2) (s-city-loc l22 c2)
		(s-airport-loc l11) (s-airport-loc l21)
 )
 (:goal 
	(and (at-x x1) (at-y y1))
 )
)
