(define (problem p10)
    (:domain ctp)
    
    (:objects
        v0 v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 - vertex
        e0 e1 e2 e3 e4 e5 e6 e7 e8 e9 e10 e11 e12 e13 e14 e15 e16 e17 e18 e19 - edge)
    (:init
    
        (adjacent v0 e0) (adjacent v1 e0)
        (adjacent v0 e1) (adjacent v1 e1)
        
        (adjacent v1 e2) (adjacent v2 e2)
        (adjacent v1 e3) (adjacent v2 e3)
        
        (adjacent v2 e4) (adjacent v3 e4)
        (adjacent v2 e5) (adjacent v3 e5)
        
        (adjacent v3 e6) (adjacent v4 e6)
        (adjacent v3 e7) (adjacent v4 e7)
        
        (adjacent v4 e8) (adjacent v5 e8)
        (adjacent v4 e9) (adjacent v5 e9)
        
        (adjacent v5 e10) (adjacent v6 e10)
        (adjacent v5 e11) (adjacent v6 e11)
        
        (adjacent v6 e12) (adjacent v7 e12)
        (adjacent v6 e13) (adjacent v7 e13)
        
        (adjacent v7 e14) (adjacent v8 e14)
        (adjacent v7 e15) (adjacent v8 e15)
        
        (adjacent v8 e16) (adjacent v9 e16)
        (adjacent v8 e17) (adjacent v9 e17)
        
        (adjacent v9 e18) (adjacent v10 e18)
        (adjacent v9 e19) (adjacent v10 e19)
        
        (at v0)
        
        (oneof (traversable e0) (traversable e1))
        (oneof (traversable e2) (traversable e3))
        (oneof (traversable e4) (traversable e5))
        (oneof (traversable e6) (traversable e7))
        (oneof (traversable e8) (traversable e9))
        (oneof (traversable e10) (traversable e11))
        (oneof (traversable e12) (traversable e13))
        (oneof (traversable e14) (traversable e15))
        (oneof (traversable e16) (traversable e17))
        (oneof (traversable e18) (traversable e19))
    )
    
    (:goal (at v10))
)
