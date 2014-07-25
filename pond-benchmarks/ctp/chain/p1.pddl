(define (problem p1)
    (:domain ctp)
    (:objects
        v0 v1 - vertex
        e0 e1 - edge)
    (:init
    
        (adjacent v0 e0) (adjacent v1 e0)
        (adjacent v0 e1) (adjacent v1 e1)
        
        (at v0)
        
        (oneof (traversable e0) (traversable e1))
    )
    
    (:goal (at v1))
)

