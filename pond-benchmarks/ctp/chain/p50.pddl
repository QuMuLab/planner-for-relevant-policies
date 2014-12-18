(define (problem p50)
    (:domain ctp)
    
    (:objects
        v0 v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 v11 v12 v13 v14 v15 v16 v17 v18 v19 v20 v21 v22 v23 v24 v25 v26 v27 v28 v29 v30 v31 v32 v33 v34 v35 v36 v37 v38 v39 v40 v41 v42 v43 v44 v45 v46 v47 v48 v49 v50 - vertex
        e0 e1 e2 e3 e4 e5 e6 e7 e8 e9 e10 e11 e12 e13 e14 e15 e16 e17 e18 e19 e20 e21 e22 e23 e24 e25 e26 e27 e28 e29 e30 e31 e32 e33 e34 e35 e36 e37 e38 e39 e40 e41 e42 e43 e44 e45 e46 e47 e48 e49 e50 e51 e52 e53 e54 e55 e56 e57 e58 e59 e60 e61 e62 e63 e64 e65 e66 e67 e68 e69 e70 e71 e72 e73 e74 e75 e76 e77 e78 e79 e80 e81 e82 e83 e84 e85 e86 e87 e88 e89 e90 e91 e92 e93 e94 e95 e96 e97 e98 e99 - edge)
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
        
        (adjacent v10 e20) (adjacent v11 e20)
        (adjacent v10 e21) (adjacent v11 e21)
        
        (adjacent v11 e22) (adjacent v12 e22)
        (adjacent v11 e23) (adjacent v12 e23)
        
        (adjacent v12 e24) (adjacent v13 e24)
        (adjacent v12 e25) (adjacent v13 e25)
        
        (adjacent v13 e26) (adjacent v14 e26)
        (adjacent v13 e27) (adjacent v14 e27)
        
        (adjacent v14 e28) (adjacent v15 e28)
        (adjacent v14 e29) (adjacent v15 e29)
        
        (adjacent v15 e30) (adjacent v16 e30)
        (adjacent v15 e31) (adjacent v16 e31)
        
        (adjacent v16 e32) (adjacent v17 e32)
        (adjacent v16 e33) (adjacent v17 e33)
        
        (adjacent v17 e34) (adjacent v18 e34)
        (adjacent v17 e35) (adjacent v18 e35)
        
        (adjacent v18 e36) (adjacent v19 e36)
        (adjacent v18 e37) (adjacent v19 e37)
        
        (adjacent v19 e38) (adjacent v20 e38)
        (adjacent v19 e39) (adjacent v20 e39)
        
        (adjacent v20 e40) (adjacent v21 e40)
        (adjacent v20 e41) (adjacent v21 e41)
        
        (adjacent v21 e42) (adjacent v22 e42)
        (adjacent v21 e43) (adjacent v22 e43)
        
        (adjacent v22 e44) (adjacent v23 e44)
        (adjacent v22 e45) (adjacent v23 e45)
        
        (adjacent v23 e46) (adjacent v24 e46)
        (adjacent v23 e47) (adjacent v24 e47)
        
        (adjacent v24 e48) (adjacent v25 e48)
        (adjacent v24 e49) (adjacent v25 e49)
        
        (adjacent v25 e50) (adjacent v26 e50)
        (adjacent v25 e51) (adjacent v26 e51)
        
        (adjacent v26 e52) (adjacent v27 e52)
        (adjacent v26 e53) (adjacent v27 e53)
        
        (adjacent v27 e54) (adjacent v28 e54)
        (adjacent v27 e55) (adjacent v28 e55)
        
        (adjacent v28 e56) (adjacent v29 e56)
        (adjacent v28 e57) (adjacent v29 e57)
        
        (adjacent v29 e58) (adjacent v30 e58)
        (adjacent v29 e59) (adjacent v30 e59)
        
        (adjacent v30 e60) (adjacent v31 e60)
        (adjacent v30 e61) (adjacent v31 e61)
        
        (adjacent v31 e62) (adjacent v32 e62)
        (adjacent v31 e63) (adjacent v32 e63)
        
        (adjacent v32 e64) (adjacent v33 e64)
        (adjacent v32 e65) (adjacent v33 e65)
        
        (adjacent v33 e66) (adjacent v34 e66)
        (adjacent v33 e67) (adjacent v34 e67)
        
        (adjacent v34 e68) (adjacent v35 e68)
        (adjacent v34 e69) (adjacent v35 e69)
        
        (adjacent v35 e70) (adjacent v36 e70)
        (adjacent v35 e71) (adjacent v36 e71)
        
        (adjacent v36 e72) (adjacent v37 e72)
        (adjacent v36 e73) (adjacent v37 e73)
        
        (adjacent v37 e74) (adjacent v38 e74)
        (adjacent v37 e75) (adjacent v38 e75)
        
        (adjacent v38 e76) (adjacent v39 e76)
        (adjacent v38 e77) (adjacent v39 e77)
        
        (adjacent v39 e78) (adjacent v40 e78)
        (adjacent v39 e79) (adjacent v40 e79)
        
        (adjacent v40 e80) (adjacent v41 e80)
        (adjacent v40 e81) (adjacent v41 e81)
        
        (adjacent v41 e82) (adjacent v42 e82)
        (adjacent v41 e83) (adjacent v42 e83)
        
        (adjacent v42 e84) (adjacent v43 e84)
        (adjacent v42 e85) (adjacent v43 e85)
        
        (adjacent v43 e86) (adjacent v44 e86)
        (adjacent v43 e87) (adjacent v44 e87)
        
        (adjacent v44 e88) (adjacent v45 e88)
        (adjacent v44 e89) (adjacent v45 e89)
        
        (adjacent v45 e90) (adjacent v46 e90)
        (adjacent v45 e91) (adjacent v46 e91)
        
        (adjacent v46 e92) (adjacent v47 e92)
        (adjacent v46 e93) (adjacent v47 e93)
        
        (adjacent v47 e94) (adjacent v48 e94)
        (adjacent v47 e95) (adjacent v48 e95)
        
        (adjacent v48 e96) (adjacent v49 e96)
        (adjacent v48 e97) (adjacent v49 e97)
        
        (adjacent v49 e98) (adjacent v50 e98)
        (adjacent v49 e99) (adjacent v50 e99)
        
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
        (oneof (traversable e20) (traversable e21))
        (oneof (traversable e22) (traversable e23))
        (oneof (traversable e24) (traversable e25))
        (oneof (traversable e26) (traversable e27))
        (oneof (traversable e28) (traversable e29))
        (oneof (traversable e30) (traversable e31))
        (oneof (traversable e32) (traversable e33))
        (oneof (traversable e34) (traversable e35))
        (oneof (traversable e36) (traversable e37))
        (oneof (traversable e38) (traversable e39))
        (oneof (traversable e40) (traversable e41))
        (oneof (traversable e42) (traversable e43))
        (oneof (traversable e44) (traversable e45))
        (oneof (traversable e46) (traversable e47))
        (oneof (traversable e48) (traversable e49))
        (oneof (traversable e50) (traversable e51))
        (oneof (traversable e52) (traversable e53))
        (oneof (traversable e54) (traversable e55))
        (oneof (traversable e56) (traversable e57))
        (oneof (traversable e58) (traversable e59))
        (oneof (traversable e60) (traversable e61))
        (oneof (traversable e62) (traversable e63))
        (oneof (traversable e64) (traversable e65))
        (oneof (traversable e66) (traversable e67))
        (oneof (traversable e68) (traversable e69))
        (oneof (traversable e70) (traversable e71))
        (oneof (traversable e72) (traversable e73))
        (oneof (traversable e74) (traversable e75))
        (oneof (traversable e76) (traversable e77))
        (oneof (traversable e78) (traversable e79))
        (oneof (traversable e80) (traversable e81))
        (oneof (traversable e82) (traversable e83))
        (oneof (traversable e84) (traversable e85))
        (oneof (traversable e86) (traversable e87))
        (oneof (traversable e88) (traversable e89))
        (oneof (traversable e90) (traversable e91))
        (oneof (traversable e92) (traversable e93))
        (oneof (traversable e94) (traversable e95))
        (oneof (traversable e96) (traversable e97))
        (oneof (traversable e98) (traversable e99))
    )
    
    (:goal (at v50))
)
