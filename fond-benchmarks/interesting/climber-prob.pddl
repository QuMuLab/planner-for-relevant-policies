(define (problem climber-problem)
  (:domain climber)
  (:init (on-roof) (alive) (ladder-on-ground))
  (:goal (and (on-ground) (alive))))
