(define (over-or-under num1 num2)
  (if (< num1 num2)
      -1
      (if (= num1 num2)
          0
          1)))

(define (make-adder num)
  (lambda (inc) (+ inc num)))

(define (composed f g) (lambda (x) (f (g x))))

(define (square n) (* n n))

(define (pow base exp)
  (cond 
    ((= exp 0)
     1)
    ((= exp 1)
     base)
    ((odd? exp)
     (* base (pow base (- exp 1))))
    ((even? exp)
     (let ((sqrt (pow base (/ exp 2))))
       (* sqrt sqrt)))))
