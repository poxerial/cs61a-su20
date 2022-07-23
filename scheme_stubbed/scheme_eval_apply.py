import sys
import os
from unittest.util import strclass

sys.path.append("scheme_reader")

from pair import *
from scheme_utils import *
from scheme_builtins import *
from ucb import main, trace

import scheme_forms

##############
# Eval/Apply #
##############

def __main__():
    print('begin!')
    breakpoint
    expr = read_line('(define (f x) (* x x)')
    f = Frame(None)
    scheme_eval(expr, f)
    val = scheme_eval(read_line())
    print(val)

def scheme_eval(expr, env, _=None):  # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in Frame ENV.

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    # BEGIN Problem 1/2
    other_builtins = {}

    def builtin_find(name):
        for t in BUILTINS:
            if t[0] == name:
                return t
        return None

    def other_builtin(name):
        def add(py_func):
            other_builtins[name]=py_func
            return py_func
        return add

    @other_builtin('lambda')
    def scheme_lambda(expr_rest, env:Frame):
        formals = expr_rest.first
        body = expr_rest.rest
        if body == nil:
            raise SchemeError('Invalid lambda expressing!')
        return LambdaProcedure(formals, body, env)
        
    @other_builtin('define')
    def scheme_define(expr_rest, env:Frame):
        name = expr_rest.first
        if type(name) == Pair:
            formals = name.rest
            name = name.first
            if type(name) != str:
                raise SchemeError('Invalid defining!')
            body = expr_rest.rest
            func = LambdaProcedure(formals, body, env)
            env.define(name, func)
            func.env.define(name, func)
            return name
        if type(name) != str or name in other_builtins or builtin_find(name):
            raise SchemeError('Invalide define name ' + str(name))
        value = scheme_eval(expr_rest.rest.first, env)
        env.define(name, value)
        return name

    @other_builtin('eval')
    def eval_in_scheme(expr_rest, env:Frame):
        return scheme_eval(scheme_eval(expr_rest.first, env), env)

    @other_builtin('quote')
    def scheme_quote(expr_rest, env:Frame):
        return expr_rest.first
    
    @other_builtin('begin')
    def scheme_begin(expr_rest, env:Frame):
        rt = None
        while expr_rest != nil:
            rt = scheme_eval(expr_rest.first, env)
            expr_rest = expr_rest.rest
        return rt

    if type(expr) != Pair:
        if type(expr)==str:
            l = env.find(expr)
            if l:
                return l
            val = env.find(expr)
            if val != None:
               return val
            if builtin_find(expr):
                return '#'+expr
            else:
                raise SchemeError('Undefined name: ' + str(expr)) 
        return expr
    
    operator_name = expr.first
    if type(operator_name) != str:
        if type(operator_name) == Pair:
            prcd = scheme_eval(operator_name, env)
            return complete_apply(prcd, expr.rest, env)
        else:
            raise SchemeError('No valid operator!')

    if operator_name in other_builtins:
        return other_builtins[operator_name](expr.rest, env)

    prcd = env.find(operator_name)
    if prcd:
        if type(prcd) == LambdaProcedure:
            return complete_apply(prcd, expr.rest, env)

    args = []
    temp = expr.rest
    while type(temp) == Pair:
        args.append(scheme_eval(temp.first, env))
        temp = temp.rest

    t = builtin_find(operator_name)
    if t:
        try:
            if t[3]:
                return t[1](*args, env=env)
            else:
                return t[1](*args)
        except TypeError:
            raise SchemeError(TypeError)
    raise SchemeError('Undefined operator ' + str(operator_name) + '!')
    # END Problem 1/2


def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    Frame ENV, the current environment."""
    # BEGIN Problem 1/2
    py_args = [] 
    while args != nil:
        py_args.append(args.first)
        args=args.rest
    try:
        if procedure.expect_env:
            return procedure.py_func(*py_args, env=env)
        else:
            return procedure.py_func(*py_args)
    except TypeError:
        raise (SchemeError(TypeError))
    # END Problem 1/2


##################
# Tail Recursion #
##################

# Make classes/functions for creating tail recursive programs here!
# BEGIN Problem EC 1
# END Problem EC 1


def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not Unevaluated.
    Right now it just calls scheme_apply, but you will need to change this
    if you attempt the extra credit."""
    validate_procedure(procedure)
    # BEGIN
    if type(procedure) == BuiltinProcedure:
        scheme_apply(procedure, args, env)
    elif type(procedure) == LambdaProcedure:
        func_frame = Frame(env)

        prcd_env = procedure.env
        while prcd_env != None:
            for key in prcd_env.local_vals:
                func_frame.local_vals[key]=prcd_env.local_vals[key]
            prcd_env = prcd_env.parent

        formals = procedure.formals
        while args != nil:
            if formals == nil:
                raise SchemeError('Invalid args parsed to procedure!')
            func_frame.define(formals.first, scheme_eval(args.first, func_frame))
            args = args.rest
            formals = formals.rest
        if formals != nil:
            raise SchemeError('Invalid args parsed to procedure!')
        val = scheme_eval(procedure.body.first, func_frame)
        temp = procedure.body.rest
        if temp != nil:
            val = scheme_eval(temp.first, func_frame)
            temp = temp.rest
        return val

    # END
def line_eval(expr:str, frame=Frame(None)):
    return scheme_eval(read_line(expr), frame)

@main
def test():
    expr = read_line('''(define (outer-func x y)
   (define (inner z x)
     (+ x (* y 2) (* z 3)))
   inner)''')
    f =Frame(None)
    scheme_eval(expr, f)
    print(line_eval('((outer-func 1 2) 1 10)', f))
