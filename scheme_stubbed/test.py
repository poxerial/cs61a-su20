from scheme_reader import *
from scheme import *
expr = read_line('(define size 2)')
print(scheme_eval(expr, create_global_frame()))