(define (domain hydraulic-planning)
  (:requirements :typing :adl)
  (:types node valve - object
          tank jet junction - node)
  (:predicates (open ?v - valve)
	       (stuck ?v - valve)
	       (pressurized ?n - node)
	       (full ?n - node)
               (link ?n1 ?n2 - node ?v - valve))

  (:action switchon
   :parameters (?v - valve ?from ?to - node)
   :precondition (and (not (stuck ?v))
                      (link ?from ?to ?v)
                      (pressurized ?from)
                      )
   :effect       (and (open ?v)
                      (pressurized ?to)
                      )
   )

)
