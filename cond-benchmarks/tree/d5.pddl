(define (domain tree_10_3_4)
  (:requirements :typing :non-deterministic :conditional-effects)
  (:types level db)
  (:constants L0 L1 L2 L3 L4 L5 L6 L7 L8 L9 L10 - level db0 db1 db2 db3 db4 db5 db6 db7 db8 db9 db10 - db)
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
  (:action left_4_0
    :precondition (and (at L4) (noise db0))
    :effect (and (at L5) (not (at L4)))
  )
  (:action left_4_1
    :precondition (and (at L4) (noise db1))
    :effect (oneof
               (and (at L5) (not (at L4)))
               (and (at L3) (not (at L4)) (when (bit L4) (and (not (bit L4)) (noise db0) (not (noise db1))))))
  )
  (:action left_4_2
    :precondition (and (at L4) (noise db2))
    :effect (oneof
               (and (at L5) (not (at L4)))
               (and (at L3) (not (at L4)) (when (bit L4) (and (not (bit L4)) (noise db1) (not (noise db2))))))
  )
  (:action left_4_3
    :precondition (and (at L4) (noise db3))
    :effect (oneof
               (and (at L5) (not (at L4)))
               (and (at L3) (not (at L4)) (when (bit L4) (and (not (bit L4)) (noise db2) (not (noise db3))))))
  )
  (:action left_4_4
    :precondition (and (at L4) (noise db4))
    :effect (oneof
               (and (at L5) (not (at L4)))
               (and (at L3) (not (at L4)) (when (bit L4) (and (not (bit L4)) (noise db3) (not (noise db4))))))
  )
  (:action left_5_0
    :precondition (and (at L5) (noise db0))
    :effect (and (at L6) (not (at L5)))
  )
  (:action left_5_1
    :precondition (and (at L5) (noise db1))
    :effect (oneof
               (and (at L6) (not (at L5)))
               (and (at L4) (not (at L5)) (when (bit L5) (and (not (bit L5)) (noise db0) (not (noise db1))))))
  )
  (:action left_5_2
    :precondition (and (at L5) (noise db2))
    :effect (oneof
               (and (at L6) (not (at L5)))
               (and (at L4) (not (at L5)) (when (bit L5) (and (not (bit L5)) (noise db1) (not (noise db2))))))
  )
  (:action left_5_3
    :precondition (and (at L5) (noise db3))
    :effect (oneof
               (and (at L6) (not (at L5)))
               (and (at L4) (not (at L5)) (when (bit L5) (and (not (bit L5)) (noise db2) (not (noise db3))))))
  )
  (:action left_5_4
    :precondition (and (at L5) (noise db4))
    :effect (oneof
               (and (at L6) (not (at L5)))
               (and (at L4) (not (at L5)) (when (bit L5) (and (not (bit L5)) (noise db3) (not (noise db4))))))
  )
  (:action left_5_5
    :precondition (and (at L5) (noise db5))
    :effect (oneof
               (and (at L6) (not (at L5)))
               (and (at L4) (not (at L5)) (when (bit L5) (and (not (bit L5)) (noise db4) (not (noise db5))))))
  )
  (:action left_6_0
    :precondition (and (at L6) (noise db0))
    :effect (and (at L7) (not (at L6)))
  )
  (:action left_6_1
    :precondition (and (at L6) (noise db1))
    :effect (oneof
               (and (at L7) (not (at L6)))
               (and (at L5) (not (at L6)) (when (bit L6) (and (not (bit L6)) (noise db0) (not (noise db1))))))
  )
  (:action left_6_2
    :precondition (and (at L6) (noise db2))
    :effect (oneof
               (and (at L7) (not (at L6)))
               (and (at L5) (not (at L6)) (when (bit L6) (and (not (bit L6)) (noise db1) (not (noise db2))))))
  )
  (:action left_6_3
    :precondition (and (at L6) (noise db3))
    :effect (oneof
               (and (at L7) (not (at L6)))
               (and (at L5) (not (at L6)) (when (bit L6) (and (not (bit L6)) (noise db2) (not (noise db3))))))
  )
  (:action left_6_4
    :precondition (and (at L6) (noise db4))
    :effect (oneof
               (and (at L7) (not (at L6)))
               (and (at L5) (not (at L6)) (when (bit L6) (and (not (bit L6)) (noise db3) (not (noise db4))))))
  )
  (:action left_6_5
    :precondition (and (at L6) (noise db5))
    :effect (oneof
               (and (at L7) (not (at L6)))
               (and (at L5) (not (at L6)) (when (bit L6) (and (not (bit L6)) (noise db4) (not (noise db5))))))
  )
  (:action left_6_6
    :precondition (and (at L6) (noise db6))
    :effect (oneof
               (and (at L7) (not (at L6)))
               (and (at L5) (not (at L6)) (when (bit L6) (and (not (bit L6)) (noise db5) (not (noise db6))))))
  )
  (:action left_7_0
    :precondition (and (at L7) (noise db0))
    :effect (and (at L8) (not (at L7)))
  )
  (:action left_7_1
    :precondition (and (at L7) (noise db1))
    :effect (oneof
               (and (at L8) (not (at L7)))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db0) (not (noise db1))))))
  )
  (:action left_7_2
    :precondition (and (at L7) (noise db2))
    :effect (oneof
               (and (at L8) (not (at L7)))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db1) (not (noise db2))))))
  )
  (:action left_7_3
    :precondition (and (at L7) (noise db3))
    :effect (oneof
               (and (at L8) (not (at L7)))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db2) (not (noise db3))))))
  )
  (:action left_7_4
    :precondition (and (at L7) (noise db4))
    :effect (oneof
               (and (at L8) (not (at L7)))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db3) (not (noise db4))))))
  )
  (:action left_7_5
    :precondition (and (at L7) (noise db5))
    :effect (oneof
               (and (at L8) (not (at L7)))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db4) (not (noise db5))))))
  )
  (:action left_7_6
    :precondition (and (at L7) (noise db6))
    :effect (oneof
               (and (at L8) (not (at L7)))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db5) (not (noise db6))))))
  )
  (:action left_7_7
    :precondition (and (at L7) (noise db7))
    :effect (oneof
               (and (at L8) (not (at L7)))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db6) (not (noise db7))))))
  )
  (:action left_8_0
    :precondition (and (at L8) (noise db0))
    :effect (and (at L9) (not (at L8)))
  )
  (:action left_8_1
    :precondition (and (at L8) (noise db1))
    :effect (oneof
               (and (at L9) (not (at L8)))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db0) (not (noise db1))))))
  )
  (:action left_8_2
    :precondition (and (at L8) (noise db2))
    :effect (oneof
               (and (at L9) (not (at L8)))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db1) (not (noise db2))))))
  )
  (:action left_8_3
    :precondition (and (at L8) (noise db3))
    :effect (oneof
               (and (at L9) (not (at L8)))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db2) (not (noise db3))))))
  )
  (:action left_8_4
    :precondition (and (at L8) (noise db4))
    :effect (oneof
               (and (at L9) (not (at L8)))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db3) (not (noise db4))))))
  )
  (:action left_8_5
    :precondition (and (at L8) (noise db5))
    :effect (oneof
               (and (at L9) (not (at L8)))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db4) (not (noise db5))))))
  )
  (:action left_8_6
    :precondition (and (at L8) (noise db6))
    :effect (oneof
               (and (at L9) (not (at L8)))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db5) (not (noise db6))))))
  )
  (:action left_8_7
    :precondition (and (at L8) (noise db7))
    :effect (oneof
               (and (at L9) (not (at L8)))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db6) (not (noise db7))))))
  )
  (:action left_8_8
    :precondition (and (at L8) (noise db8))
    :effect (oneof
               (and (at L9) (not (at L8)))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db7) (not (noise db8))))))
  )
  (:action left_9_0
    :precondition (and (at L9) (noise db0))
    :effect (and (at L10) (not (at L9)))
  )
  (:action left_9_1
    :precondition (and (at L9) (noise db1))
    :effect (oneof
               (and (at L10) (not (at L9)))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db0) (not (noise db1))))))
  )
  (:action left_9_2
    :precondition (and (at L9) (noise db2))
    :effect (oneof
               (and (at L10) (not (at L9)))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db1) (not (noise db2))))))
  )
  (:action left_9_3
    :precondition (and (at L9) (noise db3))
    :effect (oneof
               (and (at L10) (not (at L9)))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db2) (not (noise db3))))))
  )
  (:action left_9_4
    :precondition (and (at L9) (noise db4))
    :effect (oneof
               (and (at L10) (not (at L9)))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db3) (not (noise db4))))))
  )
  (:action left_9_5
    :precondition (and (at L9) (noise db5))
    :effect (oneof
               (and (at L10) (not (at L9)))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db4) (not (noise db5))))))
  )
  (:action left_9_6
    :precondition (and (at L9) (noise db6))
    :effect (oneof
               (and (at L10) (not (at L9)))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db5) (not (noise db6))))))
  )
  (:action left_9_7
    :precondition (and (at L9) (noise db7))
    :effect (oneof
               (and (at L10) (not (at L9)))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db6) (not (noise db7))))))
  )
  (:action left_9_8
    :precondition (and (at L9) (noise db8))
    :effect (oneof
               (and (at L10) (not (at L9)))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db7) (not (noise db8))))))
  )
  (:action left_9_9
    :precondition (and (at L9) (noise db9))
    :effect (oneof
               (and (at L10) (not (at L9)))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db8) (not (noise db9))))))
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
  (:action right_4_0
    :precondition (and (at L4) (noise db0))
    :effect (and (at L5) (not (at L4)) (noise db1) (not (noise db0)) (bit L5))
  )
  (:action right_4_1
    :precondition (and (at L4) (noise db1))
    :effect (oneof
               (and (at L5) (not (at L4)) (noise db2) (not (noise db1)) (bit L5))
               (and (at L3) (not (at L4)) (when (bit L4) (and (not (bit L4)) (noise db0) (not (noise db1))))))
  )
  (:action right_4_2
    :precondition (and (at L4) (noise db2))
    :effect (oneof
               (and (at L5) (not (at L4)) (noise db3) (not (noise db2)) (bit L5))
               (and (at L3) (not (at L4)) (when (bit L4) (and (not (bit L4)) (noise db1) (not (noise db2))))))
  )
  (:action right_4_3
    :precondition (and (at L4) (noise db3))
    :effect (oneof
               (and (at L5) (not (at L4)) (noise db4) (not (noise db3)) (bit L5))
               (and (at L3) (not (at L4)) (when (bit L4) (and (not (bit L4)) (noise db2) (not (noise db3))))))
  )
  (:action right_4_4
    :precondition (and (at L4) (noise db4))
    :effect (oneof
               (and (at L5) (not (at L4)) (noise db5) (not (noise db4)) (bit L5))
               (and (at L3) (not (at L4)) (when (bit L4) (and (not (bit L4)) (noise db3) (not (noise db4))))))
  )
  (:action right_5_0
    :precondition (and (at L5) (noise db0))
    :effect (and (at L6) (not (at L5)) (noise db1) (not (noise db0)) (bit L6))
  )
  (:action right_5_1
    :precondition (and (at L5) (noise db1))
    :effect (oneof
               (and (at L6) (not (at L5)) (noise db2) (not (noise db1)) (bit L6))
               (and (at L4) (not (at L5)) (when (bit L5) (and (not (bit L5)) (noise db0) (not (noise db1))))))
  )
  (:action right_5_2
    :precondition (and (at L5) (noise db2))
    :effect (oneof
               (and (at L6) (not (at L5)) (noise db3) (not (noise db2)) (bit L6))
               (and (at L4) (not (at L5)) (when (bit L5) (and (not (bit L5)) (noise db1) (not (noise db2))))))
  )
  (:action right_5_3
    :precondition (and (at L5) (noise db3))
    :effect (oneof
               (and (at L6) (not (at L5)) (noise db4) (not (noise db3)) (bit L6))
               (and (at L4) (not (at L5)) (when (bit L5) (and (not (bit L5)) (noise db2) (not (noise db3))))))
  )
  (:action right_5_4
    :precondition (and (at L5) (noise db4))
    :effect (oneof
               (and (at L6) (not (at L5)) (noise db5) (not (noise db4)) (bit L6))
               (and (at L4) (not (at L5)) (when (bit L5) (and (not (bit L5)) (noise db3) (not (noise db4))))))
  )
  (:action right_5_5
    :precondition (and (at L5) (noise db5))
    :effect (oneof
               (and (at L6) (not (at L5)) (noise db6) (not (noise db5)) (bit L6))
               (and (at L4) (not (at L5)) (when (bit L5) (and (not (bit L5)) (noise db4) (not (noise db5))))))
  )
  (:action right_6_0
    :precondition (and (at L6) (noise db0))
    :effect (and (at L7) (not (at L6)) (noise db1) (not (noise db0)) (bit L7))
  )
  (:action right_6_1
    :precondition (and (at L6) (noise db1))
    :effect (oneof
               (and (at L7) (not (at L6)) (noise db2) (not (noise db1)) (bit L7))
               (and (at L5) (not (at L6)) (when (bit L6) (and (not (bit L6)) (noise db0) (not (noise db1))))))
  )
  (:action right_6_2
    :precondition (and (at L6) (noise db2))
    :effect (oneof
               (and (at L7) (not (at L6)) (noise db3) (not (noise db2)) (bit L7))
               (and (at L5) (not (at L6)) (when (bit L6) (and (not (bit L6)) (noise db1) (not (noise db2))))))
  )
  (:action right_6_3
    :precondition (and (at L6) (noise db3))
    :effect (oneof
               (and (at L7) (not (at L6)) (noise db4) (not (noise db3)) (bit L7))
               (and (at L5) (not (at L6)) (when (bit L6) (and (not (bit L6)) (noise db2) (not (noise db3))))))
  )
  (:action right_6_4
    :precondition (and (at L6) (noise db4))
    :effect (oneof
               (and (at L7) (not (at L6)) (noise db5) (not (noise db4)) (bit L7))
               (and (at L5) (not (at L6)) (when (bit L6) (and (not (bit L6)) (noise db3) (not (noise db4))))))
  )
  (:action right_6_5
    :precondition (and (at L6) (noise db5))
    :effect (oneof
               (and (at L7) (not (at L6)) (noise db6) (not (noise db5)) (bit L7))
               (and (at L5) (not (at L6)) (when (bit L6) (and (not (bit L6)) (noise db4) (not (noise db5))))))
  )
  (:action right_6_6
    :precondition (and (at L6) (noise db6))
    :effect (oneof
               (and (at L7) (not (at L6)) (noise db7) (not (noise db6)) (bit L7))
               (and (at L5) (not (at L6)) (when (bit L6) (and (not (bit L6)) (noise db5) (not (noise db6))))))
  )
  (:action right_7_0
    :precondition (and (at L7) (noise db0))
    :effect (and (at L8) (not (at L7)) (noise db1) (not (noise db0)) (bit L8))
  )
  (:action right_7_1
    :precondition (and (at L7) (noise db1))
    :effect (oneof
               (and (at L8) (not (at L7)) (noise db2) (not (noise db1)) (bit L8))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db0) (not (noise db1))))))
  )
  (:action right_7_2
    :precondition (and (at L7) (noise db2))
    :effect (oneof
               (and (at L8) (not (at L7)) (noise db3) (not (noise db2)) (bit L8))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db1) (not (noise db2))))))
  )
  (:action right_7_3
    :precondition (and (at L7) (noise db3))
    :effect (oneof
               (and (at L8) (not (at L7)) (noise db4) (not (noise db3)) (bit L8))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db2) (not (noise db3))))))
  )
  (:action right_7_4
    :precondition (and (at L7) (noise db4))
    :effect (oneof
               (and (at L8) (not (at L7)) (noise db5) (not (noise db4)) (bit L8))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db3) (not (noise db4))))))
  )
  (:action right_7_5
    :precondition (and (at L7) (noise db5))
    :effect (oneof
               (and (at L8) (not (at L7)) (noise db6) (not (noise db5)) (bit L8))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db4) (not (noise db5))))))
  )
  (:action right_7_6
    :precondition (and (at L7) (noise db6))
    :effect (oneof
               (and (at L8) (not (at L7)) (noise db7) (not (noise db6)) (bit L8))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db5) (not (noise db6))))))
  )
  (:action right_7_7
    :precondition (and (at L7) (noise db7))
    :effect (oneof
               (and (at L8) (not (at L7)) (noise db8) (not (noise db7)) (bit L8))
               (and (at L6) (not (at L7)) (when (bit L7) (and (not (bit L7)) (noise db6) (not (noise db7))))))
  )
  (:action right_8_0
    :precondition (and (at L8) (noise db0))
    :effect (and (at L9) (not (at L8)) (noise db1) (not (noise db0)) (bit L9))
  )
  (:action right_8_1
    :precondition (and (at L8) (noise db1))
    :effect (oneof
               (and (at L9) (not (at L8)) (noise db2) (not (noise db1)) (bit L9))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db0) (not (noise db1))))))
  )
  (:action right_8_2
    :precondition (and (at L8) (noise db2))
    :effect (oneof
               (and (at L9) (not (at L8)) (noise db3) (not (noise db2)) (bit L9))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db1) (not (noise db2))))))
  )
  (:action right_8_3
    :precondition (and (at L8) (noise db3))
    :effect (oneof
               (and (at L9) (not (at L8)) (noise db4) (not (noise db3)) (bit L9))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db2) (not (noise db3))))))
  )
  (:action right_8_4
    :precondition (and (at L8) (noise db4))
    :effect (oneof
               (and (at L9) (not (at L8)) (noise db5) (not (noise db4)) (bit L9))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db3) (not (noise db4))))))
  )
  (:action right_8_5
    :precondition (and (at L8) (noise db5))
    :effect (oneof
               (and (at L9) (not (at L8)) (noise db6) (not (noise db5)) (bit L9))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db4) (not (noise db5))))))
  )
  (:action right_8_6
    :precondition (and (at L8) (noise db6))
    :effect (oneof
               (and (at L9) (not (at L8)) (noise db7) (not (noise db6)) (bit L9))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db5) (not (noise db6))))))
  )
  (:action right_8_7
    :precondition (and (at L8) (noise db7))
    :effect (oneof
               (and (at L9) (not (at L8)) (noise db8) (not (noise db7)) (bit L9))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db6) (not (noise db7))))))
  )
  (:action right_8_8
    :precondition (and (at L8) (noise db8))
    :effect (oneof
               (and (at L9) (not (at L8)) (noise db9) (not (noise db8)) (bit L9))
               (and (at L7) (not (at L8)) (when (bit L8) (and (not (bit L8)) (noise db7) (not (noise db8))))))
  )
  (:action right_9_0
    :precondition (and (at L9) (noise db0))
    :effect (and (at L10) (not (at L9)) (noise db1) (not (noise db0)) (bit L10))
  )
  (:action right_9_1
    :precondition (and (at L9) (noise db1))
    :effect (oneof
               (and (at L10) (not (at L9)) (noise db2) (not (noise db1)) (bit L10))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db0) (not (noise db1))))))
  )
  (:action right_9_2
    :precondition (and (at L9) (noise db2))
    :effect (oneof
               (and (at L10) (not (at L9)) (noise db3) (not (noise db2)) (bit L10))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db1) (not (noise db2))))))
  )
  (:action right_9_3
    :precondition (and (at L9) (noise db3))
    :effect (oneof
               (and (at L10) (not (at L9)) (noise db4) (not (noise db3)) (bit L10))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db2) (not (noise db3))))))
  )
  (:action right_9_4
    :precondition (and (at L9) (noise db4))
    :effect (oneof
               (and (at L10) (not (at L9)) (noise db5) (not (noise db4)) (bit L10))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db3) (not (noise db4))))))
  )
  (:action right_9_5
    :precondition (and (at L9) (noise db5))
    :effect (oneof
               (and (at L10) (not (at L9)) (noise db6) (not (noise db5)) (bit L10))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db4) (not (noise db5))))))
  )
  (:action right_9_6
    :precondition (and (at L9) (noise db6))
    :effect (oneof
               (and (at L10) (not (at L9)) (noise db7) (not (noise db6)) (bit L10))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db5) (not (noise db6))))))
  )
  (:action right_9_7
    :precondition (and (at L9) (noise db7))
    :effect (oneof
               (and (at L10) (not (at L9)) (noise db8) (not (noise db7)) (bit L10))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db6) (not (noise db7))))))
  )
  (:action right_9_8
    :precondition (and (at L9) (noise db8))
    :effect (oneof
               (and (at L10) (not (at L9)) (noise db9) (not (noise db8)) (bit L10))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db7) (not (noise db8))))))
  )
  (:action right_9_9
    :precondition (and (at L9) (noise db9))
    :effect (oneof
               (and (at L10) (not (at L9)) (noise db10) (not (noise db9)) (bit L10))
               (and (at L8) (not (at L9)) (when (bit L9) (and (not (bit L9)) (noise db8) (not (noise db9))))))
  )
)

