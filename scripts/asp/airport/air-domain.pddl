(define (domain pseudo-airport)
(:requirements :typing)
(:types location locatable gas_level distance - object
        passenger vehicle - locatable)
(:predicates (at ?o - locatable ?l - location)
             (in ?p - passenger ?v - vehicle)
             (gas ?l - location)
             (driveway ?x ?y - location ?d - distance)
             (occupied ?v - vehicle)
             (max_fuel ?v - vehicle ?g - gas_level)
             (current_fuel ?v - vehicle ?g - gas_level)
             (fuel_lost ?d - distance ?x ?y - gas_level)
)


(:action pick
 :parameters (?p - passenger ?v - vehicle ?l - location)
 :precondition (and (at ?p ?l)
                    (at ?v ?l)
                    (not (occupied ?v)) )
 :effect (and (not (at ?p ?l))
              (in ?p ?v)
              (occupied ?v) )
)


(:action drop
 :parameters (?p - passenger ?v - vehicle ?l - location)
 :precondition (and (in ?p ?v)
                    (at ?v ?l)
                    (occupied ?v) )
 :effect (and (not (in ?p ?v))
              (at ?p ?l)
              (not (occupied ?v)) )
)

(:action drive 
 :parameters (?v - vehicle ?x ?y - location ?current ?post - gas_level ?d - distance)
 :precondition (and (at ?v ?x)
                    (driveway ?x ?y ?d)
                    (current_fuel ?v ?current)
                    (fuel_lost ?d ?current ?post) )
 :effect (and (not (at ?v ?x))
              (at ?v ?y)
              (not (current_fuel ?v ?current))
              (current_fuel ?v ?post) )
)
                                  

(:action refuel	
 :parameters (?v - vehicle ?l - location ?current ?max - gas_level)
 :precondition (and (max_fuel ?v ?max)
                    (current_fuel ?v ?current)
                    (at ?v ?l)
                    (gas ?l) )
 :effect (and (not (current_fuel ?v ?current))
              (current_fuel ?v ?max) )
)

)

