(define (problem bw_21_21)
  (:domain blocks-domain)
  (:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 b15 b16 b17 b18 b19 b20 b21 - block)
  (:init (fair) (emptyhand) (on b1 b10) (on b2 b14) (on b3 b13) (on b4 b6) (on b5 b2) (on b6 b17) (on-table b7) (on b8 b19) (on-table b9) (on b10 b3) (on b11 b15) (on b12 b11) (on b13 b16) (on-table b14) (on b15 b18) (on b16 b9) (on-table b17) (on b18 b4) (on b19 b5) (on b20 b8) (on-table b21) (clear b1) (clear b7) (clear b12) (clear b20) (clear b21))
  (:goal (and (emptyhand) (on-table b1) (on b2 b11) (on b3 b7) (on-table b4) (on b5 b3) (on b6 b13) (on b7 b18) (on b8 b6) (on b9 b21) (on-table b10) (on b11 b20) (on b12 b19) (on b13 b17) (on b14 b9) (on-table b15) (on-table b16) (on b17 b1) (on b18 b14) (on b19 b2) (on-table b20) (on b21 b16) (clear b4) (clear b5) (clear b8) (clear b10) (clear b12) (clear b15)))
)
