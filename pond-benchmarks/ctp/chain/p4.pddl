(define (problem p4)
    (:domain ctp)
    
    (:objects
        v0 v1 v2 v3 v4 - vertex
        e0 e1 e2 e3 e4 e5 e6 e7 - edge)
    (:init
    
        (adjacent v0 e0) (adjacent v1 e0)
        (adjacent v0 e1) (adjacent v1 e1)
        
        (adjacent v1 e2) (adjacent v2 e2)
        (adjacent v1 e3) (adjacent v2 e3)
        
        (adjacent v2 e4) (adjacent v3 e4)
        (adjacent v2 e5) (adjacent v3 e5)
        
        (adjacent v3 e6) (adjacent v4 e6)
        (adjacent v3 e7) (adjacent v4 e7)
        
        (at v0)
        
        (oneof (traversable e0) (traversable e1))
        (oneof (traversable e2) (traversable e3))
        (oneof (traversable e4) (traversable e5))
        (oneof (traversable e6) (traversable e7))
    )
    
    (:goal (at v4))
)
