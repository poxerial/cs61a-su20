(define (f a) (if (< a 0) a (f (- a 1))))
(f 1000)