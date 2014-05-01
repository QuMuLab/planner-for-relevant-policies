(define (domain blocks-domain)

  (:requirements :non-deterministic :negative-preconditions :equality :typing)
  
  (:types block)
  
  (:predicates (holding-one) (holding-two) (holding ?b - block) (emptyhand) (on-table ?b - block) (on ?b1 ?b2 - block) (clear ?b - block)
               (switch1))
  
  (:action pick-up
    :parameters (?b1 ?b2 - block)
    :precondition (and (not (= ?b1 ?b2)) (emptyhand) (clear ?b1) (on ?b1 ?b2))
    :effect (and (clear ?b2) (not (on ?b1 ?b2))
             (oneof (and (holding-one) (holding ?b1) (not (emptyhand)) (not (clear ?b1)))
                    (on-table ?b1))
             (oneof (switch1) (not (switch1))))
  )
  
  (:action pick-up-from-table
    :parameters (?b - block)
    :precondition (and (emptyhand) (clear ?b) (on-table ?b))
    :effect (and (oneof (and) (and (holding-one) (holding ?b) (not (emptyhand)) (not (on-table ?b)) (not (clear ?b))))
             (oneof (switch1) (not (switch1))))
  )
  
  (:action put-on-block
    :parameters (?b1 ?b2 - block)
    :precondition (and (not (= ?b1 ?b2)) (holding-one) (holding ?b1) (clear ?b2))
    :effect (and (emptyhand) (clear ?b1) (not (holding-one)) (not (holding ?b1))
             (oneof (and (on ?b1 ?b2) (not (clear ?b2)))
                    (on-table ?b1))
             (oneof (switch1) (not (switch1))))
  )
  
  (:action put-down
    :parameters (?b - block)
    :precondition (and (holding-one) (holding ?b))
    :effect (and (on-table ?b) (emptyhand) (clear ?b) (not (holding-one)) (not (holding ?b))
             (oneof (switch1) (not (switch1))))
  )
  
  (:action pick-tower
    :parameters (?b1 ?b2 ?b3 - block)
    :precondition (and (emptyhand) (on ?b1 ?b2) (on ?b2 ?b3) (clear ?b1))
    :effect
      (and (oneof (and) (and (holding-two) (holding ?b2) (clear ?b3) (not (emptyhand)) (not (on ?b2 ?b3)) (not (clear ?b1))))
             (oneof (switch1) (not (switch1))))
  )
  
  (:action put-tower-on-block
    :parameters (?b1 ?b2 ?b3 - block)
    :precondition (and (holding-two) (holding ?b2) (on ?b1 ?b2) (clear ?b3))
    :effect (and (emptyhand) (not (holding-two)) (not (holding ?b2)) (clear ?b1)
             (oneof (and (on ?b2 ?b3) (not (clear ?b3)))
                    (and (on-table ?b1) (on-table ?b2) (clear ?b2) (not (on ?b1 ?b2))))
             (oneof (switch1) (not (switch1))))
  )
  
  (:action put-tower-down
    :parameters (?b1 ?b2 - block)
    :precondition (and (holding-two) (holding ?b2) (on ?b1 ?b2))
    :effect (and (on-table ?b2) (emptyhand) (not (holding-two)) (not (holding ?b2)) (clear ?b1)
             (oneof (switch1) (not (switch1))))
  )
)
