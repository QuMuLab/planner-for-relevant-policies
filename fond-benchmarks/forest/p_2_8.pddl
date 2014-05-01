(define (problem p2)
 (:domain forest)
 (:objects
           x1 y1  x2 y2  - location
		 sx1 sy1  sx2 sy2  - sub-location
 )
 (:init 
	;;;;;;;;top level grid;;;;;;;
	(at-x x1) 
	(at-y y1)
(succ-loc x1 x2)
(succ-loc y1 y2)
	(ninitialized x1 y1)
	(ninitialized x1 y2)
	(ninitialized x2 y1)
	(ninitialized x2 y2)
	;;;;;;;;subproblems;;;;;;;;;;
  (problem-at x1 y1 logistics)
  (problem-at x1 y2 logistics)
  (problem-at x2 y1 logistics)
  (problem-at x2 y2 logistics)
        ;;;;;;;;enabling constraints;;
	(enabled x1 y1)
	(solved x1 y1)
  (enables x1 y1 x1 y2)
	(solved x1 y1)
  (enables x1 y1 x2 y1)
	(solved x2 y2)
  (enables x2 y1 x2 y2)
	(solved x2 y2)
	;;;;;;;;grid sub-problem;;;;;;
	(s-init-x sx2)
	(s-init-y sy2)
	(s-goal-x sx1)
	(s-goal-y sy1)
(s-succ-loc sx1 sx2)
(s-succ-loc sy1 sy2)
	;;;;;;logistics sub-problem;;
                (s-city-loc l11 c1) (s-city-loc l12 c1)
                (s-city-loc l21 c2) (s-city-loc l22 c2)
		(s-airport-loc l11) (s-airport-loc l21)
 )
 (:goal 
	(and (at-x x2) (at-y y2))
 )
)
