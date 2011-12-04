(define (domain river)
  (:requirements :typing :strips :non-deterministic)
  (:predicates (on-near-bank) (on-far-bank) (on-island) (alive))
  (:action traverse-rocks :parameters ()
     :precondition (and (on-near-bank))
     :effect (and (not (on-near-bank))
		  (oneof
		    (on-far-bank)
		    (not (alive))
		    (on-island)
                    (on-island)))) ; We double the on-island predicate to make the probability 0.5
  (:action swim-river :parameters ()
     :precondition (and (on-near-bank))
     :effect (and (not (on-near-bank))
		  (oneof (and) (on-far-bank))))
  (:action swim-island :parameters ()
     :precondition (and (on-island))
     :effect (and (not (on-island))
		  (oneof
		    (on-far-bank)
		    (on-far-bank)
		    (on-far-bank)
		    (on-far-bank) ; We put 4 on-far-bank predicates to make the probability 0.8
		    (not (alive))))))

