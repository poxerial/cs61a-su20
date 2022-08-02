from scheme import *

expr = read_line('(define (f a) (if (< a 0) a (f (- a 1))))')
f = create_global_frame()
scheme_eval(expr, f)

print(scheme_eval(read_line('(f 1000)'), f))
print(type(scheme_eval(read_line('(f 1000)'), f)))