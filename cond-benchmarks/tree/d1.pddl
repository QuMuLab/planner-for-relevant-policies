
; IPC-2006/probabilistic/tree

(define (domain tree_2_3_4)
  (:requirements :typing :non-deterministic :conditional-effects)
  (:types level db)
  (:constants L0 L1 L2 - level db0 db1 db2 - db)
  (:predicates (at ?l - level) (bit ?l - level) (noise ?d - db))

  (:action left_0_0
    :precondition (and (at L0) (noise db0))
    :effect (and (at L1) (not (at L0)))
  )
  (:action left_1_0
    :precondition (and (at L1) (noise db0))
    :effect (and (at L2) (not (at L1)))
  )
  (:action left_1_1
    :precondition (and (at L1) (noise db1))
    :effect (oneof
               (and (at L2) (not (at L1)))
               (and (at L0) (not (at L1)) (when (bit L1) (and (not (bit L1)) (noise db0) (not (noise db1))))))
  )

  (:action right_0_0
    :precondition (and (at L0) (noise db0))
    :effect (and (at L1) (not (at L0)) (noise db1) (not (noise db0)) (bit L1))
  )
  (:action right_1_0
    :precondition (and (at L1) (noise db0))
    :effect (and (at L2) (not (at L1)) (noise db1) (not (noise db0)) (bit L2))
  )
  (:action right_1_1
    :precondition (and (at L1) (noise db1))
    :effect (oneof
               (and (at L2) (not (at L1)) (noise db2) (not (noise db1)) (bit L2))
               (and (at L0) (not (at L1)) (when (bit L1) (and (not (bit L1)) (noise db0) (not (noise db1))))))
  )
)