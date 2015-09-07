
(define
 (problem box-p03)
  (:domain boxworld)
  (:objects box0 - box
            box1 - box
            box2 - box
            box3 - box
            box4 - box
            box5 - box
            box6 - box
            box7 - box
            box8 - box
            box9 - box
            truck0 - truck
            truck1 - truck
            plane0 - plane
            truck2 - truck
            truck3 - truck
            plane1 - plane
            city0 - city
            city1 - city
            city2 - city
            city3 - city
            city4 - city
  )
  (:init (box-at-city box0 city1)
         (destination box0 city4)
         (box-at-city box1 city4)
         (destination box1 city1)
         (box-at-city box2 city2)
         (destination box2 city3)
         (box-at-city box3 city0)
         (destination box3 city1)
         (box-at-city box4 city0)
         (destination box4 city4)
         (box-at-city box5 city0)
         (destination box5 city1)
         (box-at-city box6 city0)
         (destination box6 city4)
         (box-at-city box7 city1)
         (destination box7 city0)
         (box-at-city box8 city1)
         (destination box8 city3)
         (box-at-city box9 city3)
         (destination box9 city1)
         (truck-at-city truck0 city0)
         (truck-at-city truck1 city0)
         (plane-at-city plane0 city0)
         (truck-at-city truck2 city1)
         (truck-at-city truck3 city1)
         (plane-at-city plane1 city1)
         (can-drive city0 city3)
         (can-drive city0 city1)
         (can-drive city0 city4)
         (wrong-drive1 city0 city3)
         (wrong-drive2 city0 city1)
         (wrong-drive3 city0 city4)
         (can-fly city0 city1)
         (can-drive city1 city0)
         (can-drive city1 city3)
         (can-drive city1 city4)
         (can-drive city1 city2)
         (wrong-drive1 city1 city0)
         (wrong-drive2 city1 city3)
         (wrong-drive3 city1 city4)
         (can-fly city1 city0)
         (can-drive city2 city3)
         (can-drive city2 city4)
         (can-drive city2 city1)
         (wrong-drive1 city2 city3)
         (wrong-drive2 city2 city4)
         (wrong-drive3 city2 city1)
         (can-drive city3 city0)
         (can-drive city3 city1)
         (can-drive city3 city2)
         (can-drive city3 city4)
         (wrong-drive1 city3 city0)
         (wrong-drive2 city3 city1)
         (wrong-drive3 city3 city2)
         (can-drive city4 city0)
         (can-drive city4 city1)
         (can-drive city4 city2)
         (can-drive city4 city3)
         (wrong-drive1 city4 city0)
         (wrong-drive2 city4 city1)
         (wrong-drive3 city4 city2)
  )
  (:goal (and
            (box-at-city box0 city4)
            (box-at-city box1 city1)
            (box-at-city box2 city3)
            (box-at-city box3 city1)
            (box-at-city box4 city4)
            (box-at-city box5 city1)
            (box-at-city box6 city4)
            (box-at-city box7 city0)
            (box-at-city box8 city3)
            (box-at-city box9 city1)
    )
  )
)
