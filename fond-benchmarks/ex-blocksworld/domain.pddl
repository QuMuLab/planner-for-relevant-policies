;; Authors: Michael Littman and David Weissman
;; Modified by: Blai Bonet

;; Comment: Good plans are those that avoid putting blocks on table since the probability of detonation is higher

(define (domain exploding-blocksworld)
  (:requirements :strips :typing :non-deterministic)
  (:types block)
  (:predicates (on ?b1 ?b2 - block) (on-table ?b - block) (clear ?b - block) (holding ?b - block) (emptyhand) (no-detonated ?b - block) (no-destroyed ?b - block) (no-destroyed-table) (detonated ?b - block))

  (:action pick-up
   :parameters (?b1 ?b2 - block)
   :precondition (and (emptyhand) (clear ?b1) (on ?b1 ?b2) (no-destroyed ?b1))
   :effect (and (holding ?b1) (clear ?b2) (not (emptyhand)) (not (on ?b1 ?b2)))
  )
  (:action pick-up-from-table
   :parameters (?b - block)
   :precondition (and (emptyhand) (clear ?b) (on-table ?b) (no-destroyed ?b))
   :effect (and (holding ?b) (not (emptyhand)) (not (on-table ?b)))
  )
  (:action put-down-nodet
   :parameters (?b - block)
   :precondition (and (no-detonated ?b) (holding ?b) (no-destroyed-table))
   :effect (and (emptyhand) (on-table ?b) (not (holding ?b))
                (oneof (and) (and (not (no-destroyed-table)) (not (no-detonated ?b)) (detonated ?b) )))
  )
  (:action put-down-det
   :parameters (?b - block)
   :precondition (and (detonated ?b) (holding ?b) (no-destroyed-table))
   :effect (and (emptyhand) (on-table ?b) (not (holding ?b)))
  )
  (:action put-on-block-nodet
   :parameters (?b1 ?b2 - block)
   :precondition (and (no-detonated ?b1) (holding ?b1) (clear ?b2) (no-destroyed ?b2))
   :effect (and (emptyhand) (on ?b1 ?b2) (not (holding ?b1)) (not (clear ?b2))
                (oneof (and) (and (not (no-destroyed ?b2)) (not (no-detonated ?b1)) (detonated ?b1))))
  )
  (:action put-on-block-det
   :parameters (?b1 ?b2 - block)
   :precondition (and (detonated ?b1) (holding ?b1) (clear ?b2) (no-destroyed ?b2))
   :effect (and (emptyhand) (on ?b1 ?b2) (not (holding ?b1)) (not (clear ?b2)))
  )
)

