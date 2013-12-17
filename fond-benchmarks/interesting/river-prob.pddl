(define (problem river-problem)
  (:domain river)
  (:init (on-near-bank) (alive))
  (:goal (and (on-far-bank))))
