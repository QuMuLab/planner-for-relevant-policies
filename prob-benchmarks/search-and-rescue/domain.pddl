;; -*-lisp-*-
;; Search & Rescue domain:
;;
;;   Florent Teichteil and Patrick Fabiani, 2008

(define (domain search-and-rescue)
  
  (:requirements :typing :equality :negative-preconditions
    :probabilistic-effects :disjunctive-preconditions)
  
  (:types zone)
  
  (:constants base - zone)
  
  (:predicates
    (at ?loc - zone)
    (explored ?loc - zone)
    (landable ?loc - zone)
    (human-onboard)
    (human-alive)
    (human-rescued)
    (on-ground)
    (mission-ended)
  )
  
  (:action goto_with_human
    :parameters (?prev - zone ?loc - zone)
    :precondition (and
      (not (on-ground))
      (not (at ?loc))
      (at ?prev)
      (imply (not (= ?loc base))
        (human-alive)
      )
      (human-onboard)
    )
    :effect (and
      (not (at ?prev))
      (at ?loc)
      (probabilistic 0.05 (and (not (human-alive))))
    )
  )
  (:action goto_without_human
    :parameters (?prev - zone ?loc - zone)
    :precondition (and
      (not (on-ground))
      (not (at ?loc))
      (at ?prev)
      (imply (not (= ?loc base))
        (human-alive)
      )
      (not (human-onboard))
    )
    :effect (and
      (not (at ?prev))
      (at ?loc)
    )
  )
  
  (:action explore
    :parameters (?loc - zone)
    :precondition (and
      (not (= ?loc base))
      (at ?loc)
      (not (on-ground))
      (human-alive)
    )
    :effect (and
      (explored ?loc)
      (probabilistic
        0.7 (landable ?loc)
        0.3 (not (landable ?loc))
      )
    )
  )
  
  
  (:action land-base
    :parameters (?loc - zone)
    :precondition (and
                    (at ?loc)
                    (not (on-ground))
                    (= ?loc base)
                    (human-alive)
                    (human-onboard))
    :effect (and
                (on-ground)
                (human-rescued)))

  (:action land-nonbase
    :parameters (?loc - zone)
    :precondition (and
                    (at ?loc)
                    (not (on-ground))
                    (not (human-onboard))
                    (not (= ?loc base))
                    (human-alive)
                    (landable ?loc))
    :effect (and
                (not (landable ?loc))
                (on-ground)
                (probabilistic
                    0.2 (and (not (human-alive)))
                    0.8 (human-onboard))))
  
;  (:action land
;    :parameters (?loc - zone)
;    :precondition (and
;                    (at ?loc)
;                    (not (on-ground))
;                    (imply (not (= ?loc base))
;                    (and
;                        (human-alive)
;                        (landable ?loc))))
;    :effect (and
;                (on-ground)
;                (when (not (= ?loc base))
;                      (not (landable ?loc)))
;                (when (human-alive)
;                      (and
;                            (when (and
;                                    (human-onboard)
;                                    (= ?loc base))
;                                  (and
;                                    (human-rescued)))
;                            (when (and
;                                    (not (human-onboard))
;                                    (not (= ?loc base)))
;                                  (probabilistic
;                                    0.2 (and (not (human-alive)))
;                                    0.8 (human-onboard))))))
;  )
  
  
  
  
  
  (:action takeoff
    :parameters (?loc - zone)
    :precondition (and
      (on-ground)
      (at ?loc)
      (imply (= ?loc base)
        (and
    (human-alive)
    (not (human-rescued))
  )
      )
    )
    :effect (not (on-ground))
  )
  
  (:action end-mission
    :precondition (and
        (at base)
  (or
    (human-rescued)
    (not (human-alive))
  )
      )
    :effect (mission-ended)
  )
)
