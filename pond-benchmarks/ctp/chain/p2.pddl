(define (problem p1)
    (:domain ctp)
    (:objects
        v0 v1 v2 - vertex
        e0 e1 e2 e3 - edge)
    (:init
    
        (adjacent v0 e0) (adjacent v1 e0)
        (adjacent v0 e1) (adjacent v1 e1)
        
        (adjacent v1 e2) (adjacent v2 e2)
        (adjacent v1 e3) (adjacent v2 e3)
        
        (at v0)
        
        (oneof (traversable e0) (traversable e1))
        (oneof (traversable e2) (traversable e3))
    )
    
    (:goal (at v2))
)

