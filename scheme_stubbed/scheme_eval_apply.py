import sys
import os

from pair import *
from scheme_utils import *
from scheme_builtins import *
from ucb import main, trace

import scheme_forms

##############
# Eval/Apply #
##############


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
        
    @other_builtin('define')
    def scheme_define(expr_rest, env:Frame):
        name = expr_rest.first
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
    

    if type(expr) != Pair:
        if type(expr)==str:
            l = env.find(expr)
            if l:
                return l[1] 
            if builtin_find(expr):
                return '#'+expr
            else:
                raise SchemeError('Undefined name: ' + expr) 
        return expr
    
    operator_name = expr.first
    if type(operator_name) != str:
        raise SchemeError('Undefined behavior!')

    if operator_name in other_builtins:
        return other_builtins[operator_name](expr.rest, env)

    args = []
    temp = expr.rest
    while type(temp) == Pair:
        args.append(scheme_eval(temp.first, env))
        temp = temp.rest
    operator_name = expr.first

    for t in BUILTINS:
        if t[0] == operator_name:
            try:
                if t[3]:
                    return t[1](*args, env)
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
    # END
