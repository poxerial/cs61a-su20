from scheme import *

def all_eval(exprs):
    env = create_global_frame()
    for expr in exprs:
        print(scheme_eval(read_line(expr), env))

all_eval(['(+ 1 1)'])
#all_eval(['(define square (lambda (x) (* x x)))', '(define (sum-of-squares x y) (+ (square x) (square y)))', '(sum-of-squares 3 4)'])
"""
print(scheme_eval(read_line('(f 1000)'), f))
print(type(scheme_eval(read_line('(f 1000)'), f)))
"""