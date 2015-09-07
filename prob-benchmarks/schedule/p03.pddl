  (define (problem a-schedule-problem609)
  (:domain schedule)
  (:objects P0 P1 P2 P3 P4  - packet)
  (:init 
         (alive)
         (current-phase Arrivals-and-updating)
         (need-to-process-arrivals C0)
         (status P0 Available)
         (status P1 Available)
         (status P2 Available)
         (status P3 Available)
         (status P4 Available)
         (not-dropped P0)
         (not-dropped P1)
         (not-dropped P2)
         (not-dropped P3)
         (not-dropped P4)
  )
  (:goal (and (alive) (forall (?c - class) (served ?c))))
  )
