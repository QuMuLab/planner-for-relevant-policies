(define (domain blocks-domain)

  (:requirements :non-deterministic :negative-preconditions :equality :typing)
  
  (:types block)
  
  (:predicates (fair) (holding-one) (holding-two) (holding ?b - block) (emptyhand) (on-table ?b - block) (on ?b1 ?b2 - block) (clear ?b - block))
  
  (:action pick-up_DETDUP_0
    :parameters (?b1 ?b2 - block)
    :precondition (and (not (= ?b1 ?b2)) (emptyhand) (clear ?b1) (on ?b1 ?b2) (fair))
    :effect (and (clear ?b2) (not (on ?b1 ?b2)) (holding-one) (holding ?b1) (not (emptyhand)) (not (clear ?b1)))
  )
  (:action pick-up_DETDUP_1
    :parameters (?b1 ?b2 - block)
    :precondition (and (not (= ?b1 ?b2)) (emptyhand) (clear ?b1) (on ?b1 ?b2) (fair))
    :effect (and (clear ?b2) (not (on ?b1 ?b2)) (on-table ?b1) (not (fair)))
  )
  
  (:action pick-up-from-table_DETDUP_0
    :parameters (?b - block)
    :precondition (and (emptyhand) (clear ?b) (on-table ?b) (fair))
    :effect (not (fair))
  )
  (:action pick-up-from-table_DETDUP_1
    :parameters (?b - block)
    :precondition (and (emptyhand) (clear ?b) (on-table ?b) (fair))
    :effect (and (holding-one) (holding ?b) (not (emptyhand)) (not (on-table ?b)) (not (clear ?b)))
  )
  
  (:action put-on-block_DETDUP_0
    :parameters (?b1 ?b2 - block)
    :precondition (and (not (= ?b1 ?b2)) (holding-one) (holding ?b1) (clear ?b2) (fair))
    :effect (and (emptyhand) (clear ?b1) (not (holding-one)) (not (holding ?b1)) (on ?b1 ?b2) (not (clear ?b2)))
  )
  (:action put-on-block_DETDUP_1
    :parameters (?b1 ?b2 - block)
    :precondition (and (not (= ?b1 ?b2)) (holding-one) (holding ?b1) (clear ?b2) (fair))
    :effect (and (emptyhand) (clear ?b1) (not (holding-one)) (not (holding ?b1)) (on-table ?b1) (not (fair)))
  )
  
  (:action put-down
    :parameters (?b - block)
    :precondition (and (holding-one) (holding ?b) (fair))
    :effect (and (on-table ?b) (emptyhand) (clear ?b) (not (holding-one)) (not (holding ?b)))
  )
  
  (:action pick-tower_DETDUP_0
    :parameters (?b1 ?b2 ?b3 - block)
    :precondition (and (emptyhand) (on ?b1 ?b2) (on ?b2 ?b3) (clear ?b1) (fair))
    :effect (not (fair))
  )
  (:action pick-tower_DETDUP_1
    :parameters (?b1 ?b2 ?b3 - block)
    :precondition (and (emptyhand) (on ?b1 ?b2) (on ?b2 ?b3) (clear ?b1) (fair))
    :effect (and (holding-two) (holding ?b2) (clear ?b3) (not (emptyhand)) (not (on ?b2 ?b3)) (not (clear ?b1)))
  )
  
  (:action put-tower-on-block_DETDUP_0
    :parameters (?b1 ?b2 ?b3 - block)
    :precondition (and (holding-two) (holding ?b2) (on ?b1 ?b2) (clear ?b3) (fair))
    :effect (and (emptyhand) (not (holding-two)) (not (holding ?b2)) (clear ?b1) (on ?b2 ?b3) (not (clear ?b3)))
  )
  (:action put-tower-on-block_DETDUP_1
    :parameters (?b1 ?b2 ?b3 - block)
    :precondition (and (holding-two) (holding ?b2) (on ?b1 ?b2) (clear ?b3) (fair))
    :effect (and (emptyhand) (not (holding-two)) (not (holding ?b2)) (clear ?b1) (on-table ?b1) (on-table ?b2) (clear ?b2) (not (on ?b1 ?b2)) (not (fair)))
  )
  
  (:action put-tower-down
    :parameters (?b1 ?b2 - block)
    :precondition (and (holding-two) (holding ?b2) (on ?b1 ?b2) (fair))
    :effect (and (on-table ?b2) (emptyhand) (not (holding-two)) (not (holding ?b2)) (clear ?b1))
  )
  
  (:action turn_unfair_operator
	:precondition (fair)
	:effect (and (not (fair)))
	)
	
  (:action turn_fair_operator
	:precondition (and  (not (fair)))
	:effect (and (fair) )
	)
)
