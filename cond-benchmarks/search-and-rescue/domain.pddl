
; IPC-2008/FOP/search-and-rescue

;; -*-lisp-*-
;; Search & Rescue domain:
;;
;;   Florent Teichteil and Patrick Fabiani, 2008

(define (domain search-and-rescue)
  
  (:requirements :typing :equality :negative-preconditions
    :disjunctive-preconditions :universal-preconditions
    :conditional-effects :non-deterministic)
  
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
  
  (:action goto-base
    :parameters (?old_loc ?new_loc - zone)
    :precondition (and
                    (not (on-ground))
                    (not (at ?new_loc))
                    (at ?old_loc)
                    (= ?new_loc base)
                  )
    :effect (and
    
                (at ?new_loc)
                (not (at ?old_loc))
                
                (when (and (human-onboard) (human-alive))
                      (oneof (and) (not (human-alive))))
	        )
  )
  
  (:action goto-nonbase
    :parameters (?old_loc ?new_loc - zone)
    :precondition (and
                    (not (on-ground))
                    (not (at ?new_loc))
                    (at ?old_loc)
                    (not (= ?new_loc base))
                    (human-alive)
                  )
    :effect (and
    
                (at ?new_loc)
                (not (at ?old_loc))
    
                ;(forall (?prev-loc - zone)
                ;    (when (at ?prev-loc)
                ;          (not (at ?prev-loc)))
                ;)
                
                (when (and (human-onboard) (human-alive))
                      (oneof (and) (not (human-alive))))
	        )
  )
  
  
  (:action explore
    :parameters (?loc - zone)
    :precondition (and
      (not (= ?loc base))
      (at ?loc)
      (not (on-ground))
      (human-alive)
      (not (explored ?loc))
    )
    :effect (and
                (explored ?loc)
                (oneof (landable ?loc) (not (landable ?loc)))
            )
  )
  
  (:action land-base
  
    :parameters (?loc - zone)
    
    :precondition (and
                    (at ?loc)
                    (not (on-ground))
                    (= ?loc base)
                  )
    
    :effect (and
                
                (on-ground)
                
                (when (not (= ?loc base))
                    (not (landable ?loc)))
                
                (when (human-alive)
                    (and
                        (when (and (human-onboard) (= ?loc base))
                              (human-rescued))
                            
                        (when (and (not (human-onboard)) (not (= ?loc base)))
                              (oneof (not (human-alive)) (human-onboard)))
                    )
                )
            )
  )
  
  (:action land-nonbase
  
    :parameters (?loc - zone)
    
    :precondition (and
                    (at ?loc)
                    (not (on-ground))
                    (not (= ?loc base))
                    (human-alive)
                    (landable ?loc)
                  )
    
    :effect (and
                
                (on-ground)
                
                (when (not (= ?loc base))
                    (not (landable ?loc)))
                
                (when (human-alive)
                    (and
                        (when (and (human-onboard) (= ?loc base))
                              (human-rescued))
                            
                        (when (and (not (human-onboard)) (not (= ?loc base)))
                              (oneof (not (human-alive)) (human-onboard)))
                    )
                )
            )
  )
  
  (:action takeoff-base
    :parameters (?loc - zone)
    :precondition (and
      (on-ground)
      (at ?loc)
      (= ?loc base)
      (human-alive)
	  (not (human-rescued))
    )
    :effect (not (on-ground))
  )
  
  (:action takeoff-nonbase
    :parameters (?loc - zone)
    :precondition (and
      (on-ground)
      (at ?loc)
      (not (= ?loc base))
    )
    :effect (not (on-ground))
  )
  
  (:action end-mission-alive
    :precondition (and
        (at base)
	    (human-rescued)
      )
    :effect (mission-ended)
  )
  (:action end-mission-dead
    :precondition (and
        (at base)
	    (not (human-alive))
      )
    :effect (mission-ended)
  )
)
