(define (domain triangle-tire)

  (:requirements :typing :strips :non-deterministic :conditional-effects)

  (:types location)

  (:predicates (vehicle-at ?loc - location)
               (spare-in ?loc - location)
               (road ?from - location ?to - location)
               (not-flattire))

  (:action move-car
    :parameters (?from - location ?to - location)
    :precondition (and (vehicle-at ?from) (road ?from ?to))
    :effect (when (not-flattire)
                  (and (vehicle-at ?to) (not (vehicle-at ?from))
                       (oneof (and) (not (not-flattire))))))

                 
  (:action changetire
    :parameters (?loc - location)
    :precondition (and (vehicle-at ?loc))
    :effect (when (spare-in ?loc) (and (not (spare-in ?loc)) (not-flattire))))
    
)