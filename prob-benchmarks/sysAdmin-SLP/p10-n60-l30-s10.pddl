(define (problem sysadmin-60-30-10)
  (:domain sysadmin-slp)
  (:objects comp0 comp1 comp2 comp3 comp4 comp5 comp6 comp7 comp8 comp9 comp10 comp11 comp12 comp13 comp14 comp15 comp16 comp17 comp18 comp19 comp20 comp21 comp22 comp23 comp24 comp25 comp26 comp27 comp28 comp29 comp30 comp31 comp32 comp33 comp34 comp35 comp36 comp37 comp38 comp39 comp40 comp41 comp42 comp43 comp44 comp45 comp46 comp47 comp48 comp49 comp50 comp51 comp52 comp53 comp54 comp55 comp56 comp57 comp58 comp59 - comp)
  (:init
	 (conn comp0 comp1)
	 (conn comp0 comp13)
	 (conn comp0 comp32)
	 (conn comp1 comp2)
	 (conn comp2 comp3)
	 (conn comp3 comp4)
	 (conn comp4 comp5)
	 (conn comp5 comp6)
	 (conn comp6 comp7)
	 (conn comp7 comp8)
	 (conn comp8 comp9)
	 (conn comp9 comp10)
	 (conn comp9 comp49)
	 (conn comp10 comp11)
	 (conn comp11 comp12)
	 (conn comp11 comp55)
	 (conn comp12 comp13)
	 (conn comp13 comp14)
	 (conn comp14 comp15)
	 (conn comp15 comp16)
	 (conn comp16 comp4)
	 (conn comp16 comp17)
	 (conn comp17 comp18)
	 (conn comp18 comp19)
	 (conn comp18 comp45)
	 (conn comp19 comp20)
	 (conn comp20 comp4)
	 (conn comp20 comp21)
	 (conn comp20 comp57)
	 (conn comp21 comp22)
	 (conn comp22 comp6)
	 (conn comp22 comp23)
	 (conn comp23 comp4)
	 (conn comp23 comp24)
	 (conn comp23 comp58)
	 (conn comp24 comp25)
	 (conn comp25 comp26)
	 (conn comp25 comp28)
	 (conn comp26 comp27)
	 (conn comp27 comp28)
	 (conn comp27 comp49)
	 (conn comp28 comp29)
	 (conn comp28 comp32)
	 (conn comp29 comp30)
	 (conn comp30 comp31)
	 (conn comp31 comp32)
	 (conn comp32 comp33)
	 (conn comp33 comp6)
	 (conn comp33 comp34)
	 (conn comp34 comp35)
	 (conn comp35 comp14)
	 (conn comp35 comp36)
	 (conn comp36 comp37)
	 (conn comp37 comp38)
	 (conn comp38 comp4)
	 (conn comp38 comp23)
	 (conn comp38 comp39)
	 (conn comp39 comp40)
	 (conn comp40 comp41)
	 (conn comp41 comp0)
	 (conn comp41 comp42)
	 (conn comp42 comp43)
	 (conn comp43 comp27)
	 (conn comp43 comp44)
	 (conn comp44 comp25)
	 (conn comp44 comp45)
	 (conn comp45 comp28)
	 (conn comp45 comp46)
	 (conn comp46 comp47)
	 (conn comp47 comp44)
	 (conn comp47 comp48)
	 (conn comp48 comp13)
	 (conn comp48 comp32)
	 (conn comp48 comp49)
	 (conn comp49 comp50)
	 (conn comp50 comp51)
	 (conn comp51 comp52)
	 (conn comp52 comp5)
	 (conn comp52 comp53)
	 (conn comp53 comp54)
	 (conn comp54 comp55)
	 (conn comp55 comp30)
	 (conn comp55 comp33)
	 (conn comp55 comp56)
	 (conn comp56 comp57)
	 (conn comp57 comp0)
	 (conn comp57 comp28)
	 (conn comp57 comp58)
	 (conn comp58 comp59)
	 (conn comp59 comp0)
  )
  (:goal (forall (?c - comp)
                 (up ?c)))
  (:goal-reward 500)
 (:metric maximize (reward))
)
