(define (problem bw_20_20)
  (:domain blocks-domain)
  (:objects b1 b2 b3 b4 b5 b6 b7 b8 b9 b10 b11 b12 b13 b14 b15 b16 b17 b18 b19 b20 - block)
  (:init (fair) (emptyhand) (on b1 b13) (on b2 b12) (on b3 b16) (on b4 b1) (on b5 b20) (on-table b6) (on b7 b5) (on-table b8) (on b9 b2) (on b10 b3) (on b11 b10) (on b12 b15) (on-table b13) (on b14 b17) (on b15 b8) (on-table b16) (on b17 b18) (on b18 b4) (on b19 b7) (on-table b20) (clear b6) (clear b9) (clear b11) (clear b14) (clear b19))
  (:goal (and (emptyhand) (on b1 b9) (on-table b2) (on b3 b11) (on b4 b16) (on b5 b7) (on b6 b4) (on b7 b20) (on-table b8) (on b9 b18) (on b10 b2) (on b11 b19) (on b12 b8) (on-table b13) (on-table b14) (on b15 b17) (on b16 b12) (on b17 b1) (on-table b18) (on b19 b15) (on b20 b14) (clear b3) (clear b5) (clear b6) (clear b10) (clear b13)))
)
