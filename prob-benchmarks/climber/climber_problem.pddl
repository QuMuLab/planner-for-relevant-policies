;; Authors: Sylvie Thiébaux and Iain Little
;; Story: You are stuck on a roof because the ladder you climbed up on
;; fell down.  There are plenty of people around; if you call out for
;; help someone will certaintly lift the ladder up again.  Or you can
;; try the climb down without it.  You aren't a very good climber
;; though, so there is a 50-50 chance that you will fall and break
;; your neck if you go it alone.  What do you do?

(define (problem climber-problem)
  (:domain climber)
  (:init (on-roof) (alive) (ladder-on-ground))
  (:goal (and (on-ground) (alive))))