(define (problem elev_7_7_3_4_28524)
  (:domain elevators)
  (:objects f2 f3 f4 f5 f6 f7 - floor p2 p3 p4 p5 p6 p7 - pos e1 e2 e3 - elevator c1 c2 c3 c4 - coin)
  (:init (at f1 p1) (dec_f f2 f1) (dec_f f3 f2) (dec_f f4 f3) (dec_f f5 f4) (dec_f f6 f5) (dec_f f7 f6) (dec_p p2 p1) (dec_p p3 p2) (dec_p p4 p3) (dec_p p5 p4) (dec_p p6 p5) (dec_p p7 p6) (shaft e1 p7) (in e1 f2) (shaft e2 p2) (in e2 f7) (shaft e3 p3) (in e3 f1) (coin-at c1 f5 p3) (coin-at c2 f2 p4) (coin-at c3 f5 p7) (coin-at c4 f1 p5) (gate f3 p2) (gate f3 p4) (gate f3 p5) (gate f3 p7) (gate f4 p2) (gate f4 p5) (gate f4 p6) (gate f5 p4) (gate f5 p5) (gate f7 p2) (gate f7 p3) (gate f7 p5) (gate f7 p6))
  (:goal (and (have c1) (have c2) (have c3) (have c4)))
)
