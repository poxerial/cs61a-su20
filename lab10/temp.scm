(define (enumerate s)
  ; BEGIN PROBLEM 15
  (define (emnumerate_core s n)
    (if (null? s)
        nil
        (cons (cons n (car s))
              (emnumerate_core (cdr s) (+ n 1)))))
(emnumerate_core s 0))

(enumerate '(3 4 5 6))
