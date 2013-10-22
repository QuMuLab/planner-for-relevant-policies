(define (domain tree_4_3_4)
  (:requirements :typing :non-deterministic :conditional-effects)
  (:types level db)
  (:constants L0 L1 L2 L3 L4 - level db0 db1 db2 db3 db4 - db)
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
  (:action left_2_0
    :precondition (and (at L2) (noise db0))
    :effect (and (at L3) (not (at L2)))
  )
  (:action left_2_1
    :precondition (and (at L2) (noise db1))
    :effect (oneof
               (and (at L3) (not (at L2)))
               (and (at L1) (not (at L2)) (when (bit L2) (and (not (bit L2)) (noise db0) (not (noise db1))))))
  )
  (:action left_2_2
    :precondition (and (at L2) (noise db2))
    :effect (oneof
               (and (at L3) (not (at L2)))
               (and (at L1) (not (at L2)) (when (bit L2) (and (not (bit L2)) (noise db1) (not (noise db2))))))
  )
  (:action left_3_0
    :precondition (and (at L3) (noise db0))
    :effect (and (at L4) (not (at L3)))
  )
  (:action left_3_1
    :precondition (and (at L3) (noise db1))
    :effect (oneof
               (and (at L4) (not (at L3)))
               (and (at L2) (not (at L3)) (when (bit L3) (and (not (bit L3)) (noise db0) (not (noise db1))))))
  )
  (:action left_3_2
    :precondition (and (at L3) (noise db2))
    :effect (oneof
               (and (at L4) (not (at L3)))
               (and (at L2) (not (at L3)) (when (bit L3) (and (not (bit L3)) (noise db1) (not (noise db2))))))
  )
  (:action left_3_3
    :precondition (and (at L3) (noise db3))
    :effect (oneof
               (and (at L4) (not (at L3)))
               (and (at L2) (not (at L3)) (when (bit L3) (and (not (bit L3)) (noise db2) (not (noise db3))))))
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
  (:action right_2_0
    :precondition (and (at L2) (noise db0))
    :effect (and (at L3) (not (at L2)) (noise db1) (not (noise db0)) (bit L3))
  )
  (:action right_2_1
    :precondition (and (at L2) (noise db1))
    :effect (oneof
               (and (at L3) (not (at L2)) (noise db2) (not (noise db1)) (bit L3))
               (and (at L1) (not (at L2)) (when (bit L2) (and (not (bit L2)) (noise db0) (not (noise db1))))))
  )
  (:action right_2_2
    :precondition (and (at L2) (noise db2))
    :effect (oneof
               (and (at L3) (not (at L2)) (noise db3) (not (noise db2)) (bit L3))
               (and (at L1) (not (at L2)) (when (bit L2) (and (not (bit L2)) (noise db1) (not (noise db2))))))
  )
  (:action right_3_0
    :precondition (and (at L3) (noise db0))
    :effect (and (at L4) (not (at L3)) (noise db1) (not (noise db0)) (bit L4))
  )
  (:action right_3_1
    :precondition (and (at L3) (noise db1))
    :effect (oneof
               (and (at L4) (not (at L3)) (noise db2) (not (noise db1)) (bit L4))
               (and (at L2) (not (at L3)) (when (bit L3) (and (not (bit L3)) (noise db0) (not (noise db1))))))
  )
  (:action right_3_2
    :precondition (and (at L3) (noise db2))
    :effect (oneof
               (and (at L4) (not (at L3)) (noise db3) (not (noise db2)) (bit L4))
               (and (at L2) (not (at L3)) (when (bit L3) (and (not (bit L3)) (noise db1) (not (noise db2))))))
  )
  (:action right_3_3
    :precondition (and (at L3) (noise db3))
    :effect (oneof
               (and (at L4) (not (at L3)) (noise db4) (not (noise db3)) (bit L4))
               (and (at L2) (not (at L3)) (when (bit L3) (and (not (bit L3)) (noise db2) (not (noise db3))))))
  )
)

