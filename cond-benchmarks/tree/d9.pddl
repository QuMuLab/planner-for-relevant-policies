(define (domain tree_18_3_4)
  (:requirements :typing :non-deterministic :conditional-effects)
  (:types level db)
  (:constants L0 L1 L2 L3 L4 L5 L6 L7 L8 L9 L10 L11 L12 L13 L14 L15 L16 L17 L18 - level db0 db1 db2 db3 db4 db5 db6 db7 db8 db9 db10 db11 db12 db13 db14 db15 db16 db17 db18 - db)
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
  (:action left_10_0
    :precondition (and (at L10) (noise db0))
    :effect (and (at L11) (not (at L10)))
  )
  (:action left_10_1
    :precondition (and (at L10) (noise db1))
    :effect (oneof
               (and (at L11) (not (at L10)))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db0) (not (noise db1))))))
  )
  (:action left_10_2
    :precondition (and (at L10) (noise db2))
    :effect (oneof
               (and (at L11) (not (at L10)))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db1) (not (noise db2))))))
  )
  (:action left_10_3
    :precondition (and (at L10) (noise db3))
    :effect (oneof
               (and (at L11) (not (at L10)))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db2) (not (noise db3))))))
  )
  (:action left_10_4
    :precondition (and (at L10) (noise db4))
    :effect (oneof
               (and (at L11) (not (at L10)))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db3) (not (noise db4))))))
  )
  (:action left_10_5
    :precondition (and (at L10) (noise db5))
    :effect (oneof
               (and (at L11) (not (at L10)))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db4) (not (noise db5))))))
  )
  (:action left_10_6
    :precondition (and (at L10) (noise db6))
    :effect (oneof
               (and (at L11) (not (at L10)))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db5) (not (noise db6))))))
  )
  (:action left_10_7
    :precondition (and (at L10) (noise db7))
    :effect (oneof
               (and (at L11) (not (at L10)))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db6) (not (noise db7))))))
  )
  (:action left_10_8
    :precondition (and (at L10) (noise db8))
    :effect (oneof
               (and (at L11) (not (at L10)))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db7) (not (noise db8))))))
  )
  (:action left_10_9
    :precondition (and (at L10) (noise db9))
    :effect (oneof
               (and (at L11) (not (at L10)))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db8) (not (noise db9))))))
  )
  (:action left_10_10
    :precondition (and (at L10) (noise db10))
    :effect (oneof
               (and (at L11) (not (at L10)))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db9) (not (noise db10))))))
  )
  (:action left_11_0
    :precondition (and (at L11) (noise db0))
    :effect (and (at L12) (not (at L11)))
  )
  (:action left_11_1
    :precondition (and (at L11) (noise db1))
    :effect (oneof
               (and (at L12) (not (at L11)))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db0) (not (noise db1))))))
  )
  (:action left_11_2
    :precondition (and (at L11) (noise db2))
    :effect (oneof
               (and (at L12) (not (at L11)))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db1) (not (noise db2))))))
  )
  (:action left_11_3
    :precondition (and (at L11) (noise db3))
    :effect (oneof
               (and (at L12) (not (at L11)))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db2) (not (noise db3))))))
  )
  (:action left_11_4
    :precondition (and (at L11) (noise db4))
    :effect (oneof
               (and (at L12) (not (at L11)))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db3) (not (noise db4))))))
  )
  (:action left_11_5
    :precondition (and (at L11) (noise db5))
    :effect (oneof
               (and (at L12) (not (at L11)))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db4) (not (noise db5))))))
  )
  (:action left_11_6
    :precondition (and (at L11) (noise db6))
    :effect (oneof
               (and (at L12) (not (at L11)))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db5) (not (noise db6))))))
  )
  (:action left_11_7
    :precondition (and (at L11) (noise db7))
    :effect (oneof
               (and (at L12) (not (at L11)))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db6) (not (noise db7))))))
  )
  (:action left_11_8
    :precondition (and (at L11) (noise db8))
    :effect (oneof
               (and (at L12) (not (at L11)))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db7) (not (noise db8))))))
  )
  (:action left_11_9
    :precondition (and (at L11) (noise db9))
    :effect (oneof
               (and (at L12) (not (at L11)))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db8) (not (noise db9))))))
  )
  (:action left_11_10
    :precondition (and (at L11) (noise db10))
    :effect (oneof
               (and (at L12) (not (at L11)))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db9) (not (noise db10))))))
  )
  (:action left_11_11
    :precondition (and (at L11) (noise db11))
    :effect (oneof
               (and (at L12) (not (at L11)))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db10) (not (noise db11))))))
  )
  (:action left_12_0
    :precondition (and (at L12) (noise db0))
    :effect (and (at L13) (not (at L12)))
  )
  (:action left_12_1
    :precondition (and (at L12) (noise db1))
    :effect (oneof
               (and (at L13) (not (at L12)))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db0) (not (noise db1))))))
  )
  (:action left_12_2
    :precondition (and (at L12) (noise db2))
    :effect (oneof
               (and (at L13) (not (at L12)))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db1) (not (noise db2))))))
  )
  (:action left_12_3
    :precondition (and (at L12) (noise db3))
    :effect (oneof
               (and (at L13) (not (at L12)))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db2) (not (noise db3))))))
  )
  (:action left_12_4
    :precondition (and (at L12) (noise db4))
    :effect (oneof
               (and (at L13) (not (at L12)))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db3) (not (noise db4))))))
  )
  (:action left_12_5
    :precondition (and (at L12) (noise db5))
    :effect (oneof
               (and (at L13) (not (at L12)))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db4) (not (noise db5))))))
  )
  (:action left_12_6
    :precondition (and (at L12) (noise db6))
    :effect (oneof
               (and (at L13) (not (at L12)))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db5) (not (noise db6))))))
  )
  (:action left_12_7
    :precondition (and (at L12) (noise db7))
    :effect (oneof
               (and (at L13) (not (at L12)))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db6) (not (noise db7))))))
  )
  (:action left_12_8
    :precondition (and (at L12) (noise db8))
    :effect (oneof
               (and (at L13) (not (at L12)))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db7) (not (noise db8))))))
  )
  (:action left_12_9
    :precondition (and (at L12) (noise db9))
    :effect (oneof
               (and (at L13) (not (at L12)))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db8) (not (noise db9))))))
  )
  (:action left_12_10
    :precondition (and (at L12) (noise db10))
    :effect (oneof
               (and (at L13) (not (at L12)))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db9) (not (noise db10))))))
  )
  (:action left_12_11
    :precondition (and (at L12) (noise db11))
    :effect (oneof
               (and (at L13) (not (at L12)))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db10) (not (noise db11))))))
  )
  (:action left_12_12
    :precondition (and (at L12) (noise db12))
    :effect (oneof
               (and (at L13) (not (at L12)))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db11) (not (noise db12))))))
  )
  (:action left_13_0
    :precondition (and (at L13) (noise db0))
    :effect (and (at L14) (not (at L13)))
  )
  (:action left_13_1
    :precondition (and (at L13) (noise db1))
    :effect (oneof
               (and (at L14) (not (at L13)))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db0) (not (noise db1))))))
  )
  (:action left_13_2
    :precondition (and (at L13) (noise db2))
    :effect (oneof
               (and (at L14) (not (at L13)))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db1) (not (noise db2))))))
  )
  (:action left_13_3
    :precondition (and (at L13) (noise db3))
    :effect (oneof
               (and (at L14) (not (at L13)))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db2) (not (noise db3))))))
  )
  (:action left_13_4
    :precondition (and (at L13) (noise db4))
    :effect (oneof
               (and (at L14) (not (at L13)))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db3) (not (noise db4))))))
  )
  (:action left_13_5
    :precondition (and (at L13) (noise db5))
    :effect (oneof
               (and (at L14) (not (at L13)))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db4) (not (noise db5))))))
  )
  (:action left_13_6
    :precondition (and (at L13) (noise db6))
    :effect (oneof
               (and (at L14) (not (at L13)))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db5) (not (noise db6))))))
  )
  (:action left_13_7
    :precondition (and (at L13) (noise db7))
    :effect (oneof
               (and (at L14) (not (at L13)))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db6) (not (noise db7))))))
  )
  (:action left_13_8
    :precondition (and (at L13) (noise db8))
    :effect (oneof
               (and (at L14) (not (at L13)))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db7) (not (noise db8))))))
  )
  (:action left_13_9
    :precondition (and (at L13) (noise db9))
    :effect (oneof
               (and (at L14) (not (at L13)))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db8) (not (noise db9))))))
  )
  (:action left_13_10
    :precondition (and (at L13) (noise db10))
    :effect (oneof
               (and (at L14) (not (at L13)))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db9) (not (noise db10))))))
  )
  (:action left_13_11
    :precondition (and (at L13) (noise db11))
    :effect (oneof
               (and (at L14) (not (at L13)))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db10) (not (noise db11))))))
  )
  (:action left_13_12
    :precondition (and (at L13) (noise db12))
    :effect (oneof
               (and (at L14) (not (at L13)))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db11) (not (noise db12))))))
  )
  (:action left_13_13
    :precondition (and (at L13) (noise db13))
    :effect (oneof
               (and (at L14) (not (at L13)))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db12) (not (noise db13))))))
  )
  (:action left_14_0
    :precondition (and (at L14) (noise db0))
    :effect (and (at L15) (not (at L14)))
  )
  (:action left_14_1
    :precondition (and (at L14) (noise db1))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db0) (not (noise db1))))))
  )
  (:action left_14_2
    :precondition (and (at L14) (noise db2))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db1) (not (noise db2))))))
  )
  (:action left_14_3
    :precondition (and (at L14) (noise db3))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db2) (not (noise db3))))))
  )
  (:action left_14_4
    :precondition (and (at L14) (noise db4))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db3) (not (noise db4))))))
  )
  (:action left_14_5
    :precondition (and (at L14) (noise db5))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db4) (not (noise db5))))))
  )
  (:action left_14_6
    :precondition (and (at L14) (noise db6))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db5) (not (noise db6))))))
  )
  (:action left_14_7
    :precondition (and (at L14) (noise db7))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db6) (not (noise db7))))))
  )
  (:action left_14_8
    :precondition (and (at L14) (noise db8))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db7) (not (noise db8))))))
  )
  (:action left_14_9
    :precondition (and (at L14) (noise db9))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db8) (not (noise db9))))))
  )
  (:action left_14_10
    :precondition (and (at L14) (noise db10))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db9) (not (noise db10))))))
  )
  (:action left_14_11
    :precondition (and (at L14) (noise db11))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db10) (not (noise db11))))))
  )
  (:action left_14_12
    :precondition (and (at L14) (noise db12))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db11) (not (noise db12))))))
  )
  (:action left_14_13
    :precondition (and (at L14) (noise db13))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db12) (not (noise db13))))))
  )
  (:action left_14_14
    :precondition (and (at L14) (noise db14))
    :effect (oneof
               (and (at L15) (not (at L14)))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db13) (not (noise db14))))))
  )
  (:action left_15_0
    :precondition (and (at L15) (noise db0))
    :effect (and (at L16) (not (at L15)))
  )
  (:action left_15_1
    :precondition (and (at L15) (noise db1))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db0) (not (noise db1))))))
  )
  (:action left_15_2
    :precondition (and (at L15) (noise db2))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db1) (not (noise db2))))))
  )
  (:action left_15_3
    :precondition (and (at L15) (noise db3))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db2) (not (noise db3))))))
  )
  (:action left_15_4
    :precondition (and (at L15) (noise db4))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db3) (not (noise db4))))))
  )
  (:action left_15_5
    :precondition (and (at L15) (noise db5))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db4) (not (noise db5))))))
  )
  (:action left_15_6
    :precondition (and (at L15) (noise db6))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db5) (not (noise db6))))))
  )
  (:action left_15_7
    :precondition (and (at L15) (noise db7))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db6) (not (noise db7))))))
  )
  (:action left_15_8
    :precondition (and (at L15) (noise db8))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db7) (not (noise db8))))))
  )
  (:action left_15_9
    :precondition (and (at L15) (noise db9))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db8) (not (noise db9))))))
  )
  (:action left_15_10
    :precondition (and (at L15) (noise db10))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db9) (not (noise db10))))))
  )
  (:action left_15_11
    :precondition (and (at L15) (noise db11))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db10) (not (noise db11))))))
  )
  (:action left_15_12
    :precondition (and (at L15) (noise db12))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db11) (not (noise db12))))))
  )
  (:action left_15_13
    :precondition (and (at L15) (noise db13))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db12) (not (noise db13))))))
  )
  (:action left_15_14
    :precondition (and (at L15) (noise db14))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db13) (not (noise db14))))))
  )
  (:action left_15_15
    :precondition (and (at L15) (noise db15))
    :effect (oneof
               (and (at L16) (not (at L15)))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db14) (not (noise db15))))))
  )
  (:action left_16_0
    :precondition (and (at L16) (noise db0))
    :effect (and (at L17) (not (at L16)))
  )
  (:action left_16_1
    :precondition (and (at L16) (noise db1))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db0) (not (noise db1))))))
  )
  (:action left_16_2
    :precondition (and (at L16) (noise db2))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db1) (not (noise db2))))))
  )
  (:action left_16_3
    :precondition (and (at L16) (noise db3))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db2) (not (noise db3))))))
  )
  (:action left_16_4
    :precondition (and (at L16) (noise db4))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db3) (not (noise db4))))))
  )
  (:action left_16_5
    :precondition (and (at L16) (noise db5))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db4) (not (noise db5))))))
  )
  (:action left_16_6
    :precondition (and (at L16) (noise db6))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db5) (not (noise db6))))))
  )
  (:action left_16_7
    :precondition (and (at L16) (noise db7))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db6) (not (noise db7))))))
  )
  (:action left_16_8
    :precondition (and (at L16) (noise db8))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db7) (not (noise db8))))))
  )
  (:action left_16_9
    :precondition (and (at L16) (noise db9))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db8) (not (noise db9))))))
  )
  (:action left_16_10
    :precondition (and (at L16) (noise db10))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db9) (not (noise db10))))))
  )
  (:action left_16_11
    :precondition (and (at L16) (noise db11))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db10) (not (noise db11))))))
  )
  (:action left_16_12
    :precondition (and (at L16) (noise db12))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db11) (not (noise db12))))))
  )
  (:action left_16_13
    :precondition (and (at L16) (noise db13))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db12) (not (noise db13))))))
  )
  (:action left_16_14
    :precondition (and (at L16) (noise db14))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db13) (not (noise db14))))))
  )
  (:action left_16_15
    :precondition (and (at L16) (noise db15))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db14) (not (noise db15))))))
  )
  (:action left_16_16
    :precondition (and (at L16) (noise db16))
    :effect (oneof
               (and (at L17) (not (at L16)))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db15) (not (noise db16))))))
  )
  (:action left_17_0
    :precondition (and (at L17) (noise db0))
    :effect (and (at L18) (not (at L17)))
  )
  (:action left_17_1
    :precondition (and (at L17) (noise db1))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db0) (not (noise db1))))))
  )
  (:action left_17_2
    :precondition (and (at L17) (noise db2))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db1) (not (noise db2))))))
  )
  (:action left_17_3
    :precondition (and (at L17) (noise db3))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db2) (not (noise db3))))))
  )
  (:action left_17_4
    :precondition (and (at L17) (noise db4))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db3) (not (noise db4))))))
  )
  (:action left_17_5
    :precondition (and (at L17) (noise db5))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db4) (not (noise db5))))))
  )
  (:action left_17_6
    :precondition (and (at L17) (noise db6))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db5) (not (noise db6))))))
  )
  (:action left_17_7
    :precondition (and (at L17) (noise db7))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db6) (not (noise db7))))))
  )
  (:action left_17_8
    :precondition (and (at L17) (noise db8))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db7) (not (noise db8))))))
  )
  (:action left_17_9
    :precondition (and (at L17) (noise db9))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db8) (not (noise db9))))))
  )
  (:action left_17_10
    :precondition (and (at L17) (noise db10))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db9) (not (noise db10))))))
  )
  (:action left_17_11
    :precondition (and (at L17) (noise db11))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db10) (not (noise db11))))))
  )
  (:action left_17_12
    :precondition (and (at L17) (noise db12))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db11) (not (noise db12))))))
  )
  (:action left_17_13
    :precondition (and (at L17) (noise db13))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db12) (not (noise db13))))))
  )
  (:action left_17_14
    :precondition (and (at L17) (noise db14))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db13) (not (noise db14))))))
  )
  (:action left_17_15
    :precondition (and (at L17) (noise db15))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db14) (not (noise db15))))))
  )
  (:action left_17_16
    :precondition (and (at L17) (noise db16))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db15) (not (noise db16))))))
  )
  (:action left_17_17
    :precondition (and (at L17) (noise db17))
    :effect (oneof
               (and (at L18) (not (at L17)))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db16) (not (noise db17))))))
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
  (:action right_10_0
    :precondition (and (at L10) (noise db0))
    :effect (and (at L11) (not (at L10)) (noise db1) (not (noise db0)) (bit L11))
  )
  (:action right_10_1
    :precondition (and (at L10) (noise db1))
    :effect (oneof
               (and (at L11) (not (at L10)) (noise db2) (not (noise db1)) (bit L11))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db0) (not (noise db1))))))
  )
  (:action right_10_2
    :precondition (and (at L10) (noise db2))
    :effect (oneof
               (and (at L11) (not (at L10)) (noise db3) (not (noise db2)) (bit L11))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db1) (not (noise db2))))))
  )
  (:action right_10_3
    :precondition (and (at L10) (noise db3))
    :effect (oneof
               (and (at L11) (not (at L10)) (noise db4) (not (noise db3)) (bit L11))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db2) (not (noise db3))))))
  )
  (:action right_10_4
    :precondition (and (at L10) (noise db4))
    :effect (oneof
               (and (at L11) (not (at L10)) (noise db5) (not (noise db4)) (bit L11))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db3) (not (noise db4))))))
  )
  (:action right_10_5
    :precondition (and (at L10) (noise db5))
    :effect (oneof
               (and (at L11) (not (at L10)) (noise db6) (not (noise db5)) (bit L11))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db4) (not (noise db5))))))
  )
  (:action right_10_6
    :precondition (and (at L10) (noise db6))
    :effect (oneof
               (and (at L11) (not (at L10)) (noise db7) (not (noise db6)) (bit L11))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db5) (not (noise db6))))))
  )
  (:action right_10_7
    :precondition (and (at L10) (noise db7))
    :effect (oneof
               (and (at L11) (not (at L10)) (noise db8) (not (noise db7)) (bit L11))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db6) (not (noise db7))))))
  )
  (:action right_10_8
    :precondition (and (at L10) (noise db8))
    :effect (oneof
               (and (at L11) (not (at L10)) (noise db9) (not (noise db8)) (bit L11))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db7) (not (noise db8))))))
  )
  (:action right_10_9
    :precondition (and (at L10) (noise db9))
    :effect (oneof
               (and (at L11) (not (at L10)) (noise db10) (not (noise db9)) (bit L11))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db8) (not (noise db9))))))
  )
  (:action right_10_10
    :precondition (and (at L10) (noise db10))
    :effect (oneof
               (and (at L11) (not (at L10)) (noise db11) (not (noise db10)) (bit L11))
               (and (at L9) (not (at L10)) (when (bit L10) (and (not (bit L10)) (noise db9) (not (noise db10))))))
  )
  (:action right_11_0
    :precondition (and (at L11) (noise db0))
    :effect (and (at L12) (not (at L11)) (noise db1) (not (noise db0)) (bit L12))
  )
  (:action right_11_1
    :precondition (and (at L11) (noise db1))
    :effect (oneof
               (and (at L12) (not (at L11)) (noise db2) (not (noise db1)) (bit L12))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db0) (not (noise db1))))))
  )
  (:action right_11_2
    :precondition (and (at L11) (noise db2))
    :effect (oneof
               (and (at L12) (not (at L11)) (noise db3) (not (noise db2)) (bit L12))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db1) (not (noise db2))))))
  )
  (:action right_11_3
    :precondition (and (at L11) (noise db3))
    :effect (oneof
               (and (at L12) (not (at L11)) (noise db4) (not (noise db3)) (bit L12))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db2) (not (noise db3))))))
  )
  (:action right_11_4
    :precondition (and (at L11) (noise db4))
    :effect (oneof
               (and (at L12) (not (at L11)) (noise db5) (not (noise db4)) (bit L12))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db3) (not (noise db4))))))
  )
  (:action right_11_5
    :precondition (and (at L11) (noise db5))
    :effect (oneof
               (and (at L12) (not (at L11)) (noise db6) (not (noise db5)) (bit L12))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db4) (not (noise db5))))))
  )
  (:action right_11_6
    :precondition (and (at L11) (noise db6))
    :effect (oneof
               (and (at L12) (not (at L11)) (noise db7) (not (noise db6)) (bit L12))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db5) (not (noise db6))))))
  )
  (:action right_11_7
    :precondition (and (at L11) (noise db7))
    :effect (oneof
               (and (at L12) (not (at L11)) (noise db8) (not (noise db7)) (bit L12))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db6) (not (noise db7))))))
  )
  (:action right_11_8
    :precondition (and (at L11) (noise db8))
    :effect (oneof
               (and (at L12) (not (at L11)) (noise db9) (not (noise db8)) (bit L12))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db7) (not (noise db8))))))
  )
  (:action right_11_9
    :precondition (and (at L11) (noise db9))
    :effect (oneof
               (and (at L12) (not (at L11)) (noise db10) (not (noise db9)) (bit L12))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db8) (not (noise db9))))))
  )
  (:action right_11_10
    :precondition (and (at L11) (noise db10))
    :effect (oneof
               (and (at L12) (not (at L11)) (noise db11) (not (noise db10)) (bit L12))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db9) (not (noise db10))))))
  )
  (:action right_11_11
    :precondition (and (at L11) (noise db11))
    :effect (oneof
               (and (at L12) (not (at L11)) (noise db12) (not (noise db11)) (bit L12))
               (and (at L10) (not (at L11)) (when (bit L11) (and (not (bit L11)) (noise db10) (not (noise db11))))))
  )
  (:action right_12_0
    :precondition (and (at L12) (noise db0))
    :effect (and (at L13) (not (at L12)) (noise db1) (not (noise db0)) (bit L13))
  )
  (:action right_12_1
    :precondition (and (at L12) (noise db1))
    :effect (oneof
               (and (at L13) (not (at L12)) (noise db2) (not (noise db1)) (bit L13))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db0) (not (noise db1))))))
  )
  (:action right_12_2
    :precondition (and (at L12) (noise db2))
    :effect (oneof
               (and (at L13) (not (at L12)) (noise db3) (not (noise db2)) (bit L13))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db1) (not (noise db2))))))
  )
  (:action right_12_3
    :precondition (and (at L12) (noise db3))
    :effect (oneof
               (and (at L13) (not (at L12)) (noise db4) (not (noise db3)) (bit L13))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db2) (not (noise db3))))))
  )
  (:action right_12_4
    :precondition (and (at L12) (noise db4))
    :effect (oneof
               (and (at L13) (not (at L12)) (noise db5) (not (noise db4)) (bit L13))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db3) (not (noise db4))))))
  )
  (:action right_12_5
    :precondition (and (at L12) (noise db5))
    :effect (oneof
               (and (at L13) (not (at L12)) (noise db6) (not (noise db5)) (bit L13))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db4) (not (noise db5))))))
  )
  (:action right_12_6
    :precondition (and (at L12) (noise db6))
    :effect (oneof
               (and (at L13) (not (at L12)) (noise db7) (not (noise db6)) (bit L13))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db5) (not (noise db6))))))
  )
  (:action right_12_7
    :precondition (and (at L12) (noise db7))
    :effect (oneof
               (and (at L13) (not (at L12)) (noise db8) (not (noise db7)) (bit L13))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db6) (not (noise db7))))))
  )
  (:action right_12_8
    :precondition (and (at L12) (noise db8))
    :effect (oneof
               (and (at L13) (not (at L12)) (noise db9) (not (noise db8)) (bit L13))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db7) (not (noise db8))))))
  )
  (:action right_12_9
    :precondition (and (at L12) (noise db9))
    :effect (oneof
               (and (at L13) (not (at L12)) (noise db10) (not (noise db9)) (bit L13))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db8) (not (noise db9))))))
  )
  (:action right_12_10
    :precondition (and (at L12) (noise db10))
    :effect (oneof
               (and (at L13) (not (at L12)) (noise db11) (not (noise db10)) (bit L13))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db9) (not (noise db10))))))
  )
  (:action right_12_11
    :precondition (and (at L12) (noise db11))
    :effect (oneof
               (and (at L13) (not (at L12)) (noise db12) (not (noise db11)) (bit L13))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db10) (not (noise db11))))))
  )
  (:action right_12_12
    :precondition (and (at L12) (noise db12))
    :effect (oneof
               (and (at L13) (not (at L12)) (noise db13) (not (noise db12)) (bit L13))
               (and (at L11) (not (at L12)) (when (bit L12) (and (not (bit L12)) (noise db11) (not (noise db12))))))
  )
  (:action right_13_0
    :precondition (and (at L13) (noise db0))
    :effect (and (at L14) (not (at L13)) (noise db1) (not (noise db0)) (bit L14))
  )
  (:action right_13_1
    :precondition (and (at L13) (noise db1))
    :effect (oneof
               (and (at L14) (not (at L13)) (noise db2) (not (noise db1)) (bit L14))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db0) (not (noise db1))))))
  )
  (:action right_13_2
    :precondition (and (at L13) (noise db2))
    :effect (oneof
               (and (at L14) (not (at L13)) (noise db3) (not (noise db2)) (bit L14))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db1) (not (noise db2))))))
  )
  (:action right_13_3
    :precondition (and (at L13) (noise db3))
    :effect (oneof
               (and (at L14) (not (at L13)) (noise db4) (not (noise db3)) (bit L14))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db2) (not (noise db3))))))
  )
  (:action right_13_4
    :precondition (and (at L13) (noise db4))
    :effect (oneof
               (and (at L14) (not (at L13)) (noise db5) (not (noise db4)) (bit L14))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db3) (not (noise db4))))))
  )
  (:action right_13_5
    :precondition (and (at L13) (noise db5))
    :effect (oneof
               (and (at L14) (not (at L13)) (noise db6) (not (noise db5)) (bit L14))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db4) (not (noise db5))))))
  )
  (:action right_13_6
    :precondition (and (at L13) (noise db6))
    :effect (oneof
               (and (at L14) (not (at L13)) (noise db7) (not (noise db6)) (bit L14))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db5) (not (noise db6))))))
  )
  (:action right_13_7
    :precondition (and (at L13) (noise db7))
    :effect (oneof
               (and (at L14) (not (at L13)) (noise db8) (not (noise db7)) (bit L14))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db6) (not (noise db7))))))
  )
  (:action right_13_8
    :precondition (and (at L13) (noise db8))
    :effect (oneof
               (and (at L14) (not (at L13)) (noise db9) (not (noise db8)) (bit L14))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db7) (not (noise db8))))))
  )
  (:action right_13_9
    :precondition (and (at L13) (noise db9))
    :effect (oneof
               (and (at L14) (not (at L13)) (noise db10) (not (noise db9)) (bit L14))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db8) (not (noise db9))))))
  )
  (:action right_13_10
    :precondition (and (at L13) (noise db10))
    :effect (oneof
               (and (at L14) (not (at L13)) (noise db11) (not (noise db10)) (bit L14))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db9) (not (noise db10))))))
  )
  (:action right_13_11
    :precondition (and (at L13) (noise db11))
    :effect (oneof
               (and (at L14) (not (at L13)) (noise db12) (not (noise db11)) (bit L14))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db10) (not (noise db11))))))
  )
  (:action right_13_12
    :precondition (and (at L13) (noise db12))
    :effect (oneof
               (and (at L14) (not (at L13)) (noise db13) (not (noise db12)) (bit L14))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db11) (not (noise db12))))))
  )
  (:action right_13_13
    :precondition (and (at L13) (noise db13))
    :effect (oneof
               (and (at L14) (not (at L13)) (noise db14) (not (noise db13)) (bit L14))
               (and (at L12) (not (at L13)) (when (bit L13) (and (not (bit L13)) (noise db12) (not (noise db13))))))
  )
  (:action right_14_0
    :precondition (and (at L14) (noise db0))
    :effect (and (at L15) (not (at L14)) (noise db1) (not (noise db0)) (bit L15))
  )
  (:action right_14_1
    :precondition (and (at L14) (noise db1))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db2) (not (noise db1)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db0) (not (noise db1))))))
  )
  (:action right_14_2
    :precondition (and (at L14) (noise db2))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db3) (not (noise db2)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db1) (not (noise db2))))))
  )
  (:action right_14_3
    :precondition (and (at L14) (noise db3))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db4) (not (noise db3)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db2) (not (noise db3))))))
  )
  (:action right_14_4
    :precondition (and (at L14) (noise db4))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db5) (not (noise db4)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db3) (not (noise db4))))))
  )
  (:action right_14_5
    :precondition (and (at L14) (noise db5))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db6) (not (noise db5)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db4) (not (noise db5))))))
  )
  (:action right_14_6
    :precondition (and (at L14) (noise db6))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db7) (not (noise db6)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db5) (not (noise db6))))))
  )
  (:action right_14_7
    :precondition (and (at L14) (noise db7))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db8) (not (noise db7)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db6) (not (noise db7))))))
  )
  (:action right_14_8
    :precondition (and (at L14) (noise db8))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db9) (not (noise db8)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db7) (not (noise db8))))))
  )
  (:action right_14_9
    :precondition (and (at L14) (noise db9))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db10) (not (noise db9)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db8) (not (noise db9))))))
  )
  (:action right_14_10
    :precondition (and (at L14) (noise db10))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db11) (not (noise db10)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db9) (not (noise db10))))))
  )
  (:action right_14_11
    :precondition (and (at L14) (noise db11))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db12) (not (noise db11)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db10) (not (noise db11))))))
  )
  (:action right_14_12
    :precondition (and (at L14) (noise db12))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db13) (not (noise db12)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db11) (not (noise db12))))))
  )
  (:action right_14_13
    :precondition (and (at L14) (noise db13))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db14) (not (noise db13)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db12) (not (noise db13))))))
  )
  (:action right_14_14
    :precondition (and (at L14) (noise db14))
    :effect (oneof
               (and (at L15) (not (at L14)) (noise db15) (not (noise db14)) (bit L15))
               (and (at L13) (not (at L14)) (when (bit L14) (and (not (bit L14)) (noise db13) (not (noise db14))))))
  )
  (:action right_15_0
    :precondition (and (at L15) (noise db0))
    :effect (and (at L16) (not (at L15)) (noise db1) (not (noise db0)) (bit L16))
  )
  (:action right_15_1
    :precondition (and (at L15) (noise db1))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db2) (not (noise db1)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db0) (not (noise db1))))))
  )
  (:action right_15_2
    :precondition (and (at L15) (noise db2))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db3) (not (noise db2)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db1) (not (noise db2))))))
  )
  (:action right_15_3
    :precondition (and (at L15) (noise db3))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db4) (not (noise db3)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db2) (not (noise db3))))))
  )
  (:action right_15_4
    :precondition (and (at L15) (noise db4))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db5) (not (noise db4)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db3) (not (noise db4))))))
  )
  (:action right_15_5
    :precondition (and (at L15) (noise db5))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db6) (not (noise db5)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db4) (not (noise db5))))))
  )
  (:action right_15_6
    :precondition (and (at L15) (noise db6))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db7) (not (noise db6)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db5) (not (noise db6))))))
  )
  (:action right_15_7
    :precondition (and (at L15) (noise db7))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db8) (not (noise db7)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db6) (not (noise db7))))))
  )
  (:action right_15_8
    :precondition (and (at L15) (noise db8))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db9) (not (noise db8)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db7) (not (noise db8))))))
  )
  (:action right_15_9
    :precondition (and (at L15) (noise db9))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db10) (not (noise db9)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db8) (not (noise db9))))))
  )
  (:action right_15_10
    :precondition (and (at L15) (noise db10))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db11) (not (noise db10)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db9) (not (noise db10))))))
  )
  (:action right_15_11
    :precondition (and (at L15) (noise db11))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db12) (not (noise db11)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db10) (not (noise db11))))))
  )
  (:action right_15_12
    :precondition (and (at L15) (noise db12))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db13) (not (noise db12)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db11) (not (noise db12))))))
  )
  (:action right_15_13
    :precondition (and (at L15) (noise db13))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db14) (not (noise db13)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db12) (not (noise db13))))))
  )
  (:action right_15_14
    :precondition (and (at L15) (noise db14))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db15) (not (noise db14)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db13) (not (noise db14))))))
  )
  (:action right_15_15
    :precondition (and (at L15) (noise db15))
    :effect (oneof
               (and (at L16) (not (at L15)) (noise db16) (not (noise db15)) (bit L16))
               (and (at L14) (not (at L15)) (when (bit L15) (and (not (bit L15)) (noise db14) (not (noise db15))))))
  )
  (:action right_16_0
    :precondition (and (at L16) (noise db0))
    :effect (and (at L17) (not (at L16)) (noise db1) (not (noise db0)) (bit L17))
  )
  (:action right_16_1
    :precondition (and (at L16) (noise db1))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db2) (not (noise db1)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db0) (not (noise db1))))))
  )
  (:action right_16_2
    :precondition (and (at L16) (noise db2))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db3) (not (noise db2)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db1) (not (noise db2))))))
  )
  (:action right_16_3
    :precondition (and (at L16) (noise db3))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db4) (not (noise db3)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db2) (not (noise db3))))))
  )
  (:action right_16_4
    :precondition (and (at L16) (noise db4))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db5) (not (noise db4)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db3) (not (noise db4))))))
  )
  (:action right_16_5
    :precondition (and (at L16) (noise db5))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db6) (not (noise db5)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db4) (not (noise db5))))))
  )
  (:action right_16_6
    :precondition (and (at L16) (noise db6))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db7) (not (noise db6)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db5) (not (noise db6))))))
  )
  (:action right_16_7
    :precondition (and (at L16) (noise db7))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db8) (not (noise db7)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db6) (not (noise db7))))))
  )
  (:action right_16_8
    :precondition (and (at L16) (noise db8))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db9) (not (noise db8)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db7) (not (noise db8))))))
  )
  (:action right_16_9
    :precondition (and (at L16) (noise db9))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db10) (not (noise db9)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db8) (not (noise db9))))))
  )
  (:action right_16_10
    :precondition (and (at L16) (noise db10))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db11) (not (noise db10)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db9) (not (noise db10))))))
  )
  (:action right_16_11
    :precondition (and (at L16) (noise db11))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db12) (not (noise db11)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db10) (not (noise db11))))))
  )
  (:action right_16_12
    :precondition (and (at L16) (noise db12))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db13) (not (noise db12)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db11) (not (noise db12))))))
  )
  (:action right_16_13
    :precondition (and (at L16) (noise db13))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db14) (not (noise db13)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db12) (not (noise db13))))))
  )
  (:action right_16_14
    :precondition (and (at L16) (noise db14))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db15) (not (noise db14)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db13) (not (noise db14))))))
  )
  (:action right_16_15
    :precondition (and (at L16) (noise db15))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db16) (not (noise db15)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db14) (not (noise db15))))))
  )
  (:action right_16_16
    :precondition (and (at L16) (noise db16))
    :effect (oneof
               (and (at L17) (not (at L16)) (noise db17) (not (noise db16)) (bit L17))
               (and (at L15) (not (at L16)) (when (bit L16) (and (not (bit L16)) (noise db15) (not (noise db16))))))
  )
  (:action right_17_0
    :precondition (and (at L17) (noise db0))
    :effect (and (at L18) (not (at L17)) (noise db1) (not (noise db0)) (bit L18))
  )
  (:action right_17_1
    :precondition (and (at L17) (noise db1))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db2) (not (noise db1)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db0) (not (noise db1))))))
  )
  (:action right_17_2
    :precondition (and (at L17) (noise db2))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db3) (not (noise db2)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db1) (not (noise db2))))))
  )
  (:action right_17_3
    :precondition (and (at L17) (noise db3))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db4) (not (noise db3)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db2) (not (noise db3))))))
  )
  (:action right_17_4
    :precondition (and (at L17) (noise db4))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db5) (not (noise db4)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db3) (not (noise db4))))))
  )
  (:action right_17_5
    :precondition (and (at L17) (noise db5))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db6) (not (noise db5)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db4) (not (noise db5))))))
  )
  (:action right_17_6
    :precondition (and (at L17) (noise db6))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db7) (not (noise db6)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db5) (not (noise db6))))))
  )
  (:action right_17_7
    :precondition (and (at L17) (noise db7))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db8) (not (noise db7)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db6) (not (noise db7))))))
  )
  (:action right_17_8
    :precondition (and (at L17) (noise db8))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db9) (not (noise db8)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db7) (not (noise db8))))))
  )
  (:action right_17_9
    :precondition (and (at L17) (noise db9))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db10) (not (noise db9)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db8) (not (noise db9))))))
  )
  (:action right_17_10
    :precondition (and (at L17) (noise db10))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db11) (not (noise db10)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db9) (not (noise db10))))))
  )
  (:action right_17_11
    :precondition (and (at L17) (noise db11))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db12) (not (noise db11)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db10) (not (noise db11))))))
  )
  (:action right_17_12
    :precondition (and (at L17) (noise db12))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db13) (not (noise db12)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db11) (not (noise db12))))))
  )
  (:action right_17_13
    :precondition (and (at L17) (noise db13))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db14) (not (noise db13)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db12) (not (noise db13))))))
  )
  (:action right_17_14
    :precondition (and (at L17) (noise db14))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db15) (not (noise db14)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db13) (not (noise db14))))))
  )
  (:action right_17_15
    :precondition (and (at L17) (noise db15))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db16) (not (noise db15)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db14) (not (noise db15))))))
  )
  (:action right_17_16
    :precondition (and (at L17) (noise db16))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db17) (not (noise db16)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db15) (not (noise db16))))))
  )
  (:action right_17_17
    :precondition (and (at L17) (noise db17))
    :effect (oneof
               (and (at L18) (not (at L17)) (noise db18) (not (noise db17)) (bit L18))
               (and (at L16) (not (at L17)) (when (bit L17) (and (not (bit L17)) (noise db16) (not (noise db17))))))
  )
)

