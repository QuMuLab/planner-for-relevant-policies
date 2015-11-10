(define (domain blocks-domain)
  (:types block location)  
  (:constants l0 l10 - location)
  (:predicates 
		(on ?bm ?bf - block)
		(clear ?x - block)
		(on-table ?x - block)
		(emptyhand)
		(holding ?b - block)
  		(adjacent ?l1 ?l2 - location)
		(at ?b - block ?l - location)
		(faulty ?b - block ?l - location)
  )
  
  (:action pick-up
      :parameters (?b1 - block)
      :precondition (at ?b1 l10)
      :effect
        (and (not (at ?b1 l10)) (oneof (holding ?b1) (and (clear ?b1) (on-table ?b1) (emptyhand) (not (holding ?b1)))))
  )

  (:action pick-up-from-table
    :parameters (?b - block)
    :precondition (and (emptyhand) (clear ?b) (on-table ?b))
    :effect (oneof (and (emptyhand) (clear ?b) (on-table ?b)) (and (holding ?b) (not (emptyhand)) (not (on-table ?b))))
  )
  
  (:action put-on-block
    :parameters (?b1 ?b2 - block)
    :precondition (and (holding ?b1) (clear ?b2))
    :effect (oneof (and (on ?b1 ?b2) (emptyhand) (clear ?b1) (not (holding ?b1)) (not (clear ?b2)))
                   (and (on-table ?b1) (emptyhand) (clear ?b1) (not (holding ?b1))))
  )
  
  (:action put-down
    :parameters (?b - block)
    :precondition (holding ?b)
    :effect (and (on-table ?b) (emptyhand) (clear ?b) (not (holding ?b)))
  )
  
  (:action pick-tower
    :parameters (?b1 ?b2 ?b3 - block)
    :precondition (and (emptyhand) (on ?b1 ?b2) (on ?b2 ?b3))
    :effect (oneof (and (holding ?b2) (clear ?b3) (not (emptyhand)) (not (on ?b2 ?b3)))
                   (and (emptyhand) (on ?b1 ?b2) (on ?b2 ?b3)))
  )
  
  (:action put-tower-on-block
    :parameters (?b1 ?b2 ?b3 - block)
    :precondition (and (holding ?b2) (on ?b1 ?b2) (clear ?b3))
    :effect (oneof (and (on ?b2 ?b3) (emptyhand) (not (holding ?b2)) (not (clear ?b3)))
                   (and (on-table ?b2) (emptyhand) (not (holding ?b2))))
  )
  
  (:action put-tower-down
    :parameters (?b1 ?b2 - block)
    :precondition (and (holding ?b2) (on ?b1 ?b2))
    :effect (and (on-table ?b2) (emptyhand) (not (holding ?b2)))
  )
  
  (:action init_pick-up
      :parameters (?b1 ?b2 - block)
      :precondition (and (emptyhand) (clear ?b1) (on ?b1 ?b2))
      :effect (and (at ?b1 l0) (not (clear ?b1)) (clear ?b2) (not (emptyhand)) (not (on ?b1 ?b2)))
   )
  
   (:action move
      :parameters (?b1 - block ?l1 ?l2 - location)
      :precondition (and (at ?b1 ?l1) (adjacent ?l1 ?l2))
      :effect (oneof (and (at ?b1 ?l2) (not (at ?b1 ?l1)))
                     (and (faulty ?b1 ?l2) (not (at ?b1 ?l1))))
    )
  
   (:action fix
      :parameters (?b - block ?l1 - location)
      :precondition (faulty ?b ?l1)
      :effect (and (at ?b ?l1) (not (faulty ?b ?l1)))
   )
)
