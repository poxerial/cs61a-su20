from scheme import *

def all_eval(exprs, env = create_global_frame()):
    for expr in exprs:
        print(scheme_eval(read_line(expr), env))

f = create_global_frame()
all_eval(["""(define (sum n total)
   (begin
      (define add (lambda (x+1 y) (sum (- x+1 1) y)))
      (or (and (zero? n) total)
          (add n (+ n total)))))""", "(sum 1001 0)"],f)


#all_eval(["""(define (sum n total)
#   (cond ((zero? n) total)
#         ((zero? 0) (sum (- n 1) (+ n total)))
#         (else 42)))""", "(sum 1001 0)"])
""""
#all_eval(['(define square (lambda (x) (* x x)))', '(define (sum-of-squares x y) (+ (square x) (square y)))', '(sum-of-squares 3 4)'])
print(scheme_eval(read_line('(f 1000)'), f))
print(type(scheme_eval(read_line('(f 1000)'), f)))
"""