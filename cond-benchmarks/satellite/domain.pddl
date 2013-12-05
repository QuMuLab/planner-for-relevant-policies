
;; IPC-2002/satellite-strips/adlSat.pddl

(define (domain satellite)
  (:requirements :non-deterministic :equality :typing :conditional-effects :negative-preconditions)
  (:types satellite direction instrument mode)
  
 (:predicates 
            (on_board ?i - instrument ?s - satellite)
	        (supports ?i - instrument ?m - mode)
	        (pointing ?s - satellite ?d - direction)
            (solar_power_avail ?s - satellite)
	        (power_avail ?s - satellite)
	        (power_on ?i - instrument)
	        (calibrated ?i - instrument)
	        (have_image ?d - direction ?m - mode)
	        (calibration_target ?i - instrument ?d - direction))
 
 

  (:action turn_to
   :parameters (?s - satellite ?d_new - direction ?d_prev - direction)
   :precondition (and (pointing ?s ?d_prev)
                      (solar_power_avail ?s)
                      (not (= ?d_new ?d_prev))
              )
   :effect (and  (pointing ?s ?d_new)
                 (not (pointing ?s ?d_prev))
                 (oneof (and) (not (solar_power_avail ?s)))
           )
  )

 
  (:action switch_on
   :parameters (?i - instrument ?s - satellite)
 
   :precondition (and (on_board ?i ?s) 
                      (power_avail ?s)
                 )
   :effect (and (power_on ?i)
                (not (calibrated ?i))
                (not (power_avail ?s))
           )
          
  )

 
  (:action switch_off
   :parameters (?i - instrument ?s - satellite)
 
   :precondition (and (on_board ?i ?s)
                      (power_on ?i) 
                  )
   :effect (and (not (power_on ?i))
                (power_avail ?s)
           )
  )
  
  (:action collect_solar
   :parameters (?s - satellite)
   :precondition (power_avail ?s)
   :effect (solar_power_avail ?s)
  )

  (:action calibrate
   :parameters (?s - satellite ?i - instrument ?d_cur - direction ?d_drift - direction)
   :precondition (and (on_board ?i ?s)
                      (calibration_target ?i ?d_cur)
                      (pointing ?s ?d_cur)
                      (power_on ?i)
                      (not (= ?d_cur ?d_drift))
                  )
   :effect (oneof (calibrated ?i) (and (pointing ?s ?d_drift) (not (solar_power_avail ?s)) (not (pointing ?s ?d_cur))))
  )


  (:action take_image
   :parameters (?s - satellite ?d - direction ?i - instrument ?m - mode)
   :precondition (and (calibrated ?i)
                      (on_board ?i ?s)
                      (supports ?i ?m)
                      (power_on ?i)
                      (pointing ?s ?d)
               )
   :effect (oneof (not (calibrated ?i))  (when (not (have_image ?d ?m)) (have_image ?d ?m)) )
  )
)

