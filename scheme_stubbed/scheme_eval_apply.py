import scheme_forms
from ucb import main, trace
from scheme_builtins import *
from scheme_utils import *
from pair import *
import sys

sys.setrecursionlimit(5000)

##############
# Eval/Apply #
##############

other_builtins = {}


def builtin_find(name):
    for t in BUILTINS:
        if t[0] == name:
            return t
    return None


def scheme_true(val):
    return not val is False


def other_builtin(name):
    def add(py_func):
        other_builtins[name] = py_func
        return py_func
    return add


@other_builtin('lambda')
def scheme_lambda(expr_rest, env: Frame):
    formals = expr_rest.first
    body = expr_rest.rest
    if body == nil:
        raise SchemeError('Invalid lambda expressing!')
    return LambdaProcedure(formals, body, env)


@other_builtin('define')
def scheme_define(expr_rest, env: Frame):
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
def eval_in_scheme(expr_rest, env: Frame):
    return scheme_eval(scheme_eval(expr_rest.first, env), env)


@other_builtin('quote')
def scheme_quote(expr_rest, env: Frame):
    return expr_rest.first


@other_builtin('begin')
def scheme_begin(expr_rest, env: Frame):
    rt = None
    while expr_rest != nil:
        rt = scheme_eval(expr_rest.first, env)
        expr_rest = expr_rest.rest
    return rt


@other_builtin('and')
def scheme_and(expr_rest, env):
    val = True
    while expr_rest != nil:
        val = scheme_eval(expr_rest.first, env)
        if not scheme_true(val):
            return val
        expr_rest = expr_rest.rest
    return val


@other_builtin('or')
def sheme_or(expr_rest, env):
    val = False
    while expr_rest != nil:
        val = scheme_eval(expr_rest.first, env)
        if scheme_true(val):
            return val
        expr_rest = expr_rest.rest
    return val


@other_builtin('if')
def scheme_if(expr_rest, env: Frame):
    if scheme_true(scheme_eval(expr_rest.first, env)):
        return scheme_eval(expr_rest.rest.first, env)
    return scheme_eval(expr_rest.rest.rest.first, env)


@other_builtin('cond')
def scheme_cond(expr_rest, env):
    while expr_rest != nil:
        temp = expr_rest.first
        val = scheme_eval(temp.first, env)
        if scheme_true(val):
            if temp.rest == nil:
                return val
            todo = temp.rest
            while todo != nil:
                val = scheme_eval(todo.first, env)
                todo = todo.rest
            return val
        expr_rest = expr_rest.rest


@other_builtin('let')
def scheme_let(expr_rest, env):
    let_frame = Frame(env)
    define_list = expr_rest.first
    while define_list != nil:
        pair = define_list.first
        let_frame.define(pair.first, scheme_eval(pair.rest.first, env))
        if pair.rest.rest != nil:
            raise SchemeError('There should be one value to asign in let form!')
        define_list = define_list.rest
    
    to_eval = expr_rest.rest
    while to_eval != nil:
        val = scheme_eval(to_eval.first, let_frame)
        to_eval = to_eval.rest
    return val


@other_builtin('mu')
def scheme_mu(expr_rest, env):
    formals = expr_rest.first
    body = expr_rest.rest
    if body == nil:
        raise SchemeError('Invalid mu expressing!')
    return MuProcedure(formals, body)
    

def scheme_eval(expr, env, _=None):  # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in Frame ENV.

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    # BEGIN Problem 1/2
    if type(expr) != Pair:
        if type(expr) == str:
            if expr == 'else':
                return True
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
        if isinstance(prcd, Procedure):
            return complete_apply(prcd, expr.rest, env)

    raise SchemeError('Undefined operator ' + str(operator_name) + '!')
    # END Problem 1/2


def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    Frame ENV, the current environment."""
    # BEGIN Problem 1/2
    py_args = []
    while args != nil:
        py_args.append(scheme_eval(args.first, env))
        args = args.rest
    try:
        if procedure.expect_env:
            return procedure.py_func(*py_args, env)
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
        return scheme_apply(procedure, args, env)
    elif type(procedure) == LambdaProcedure:
        func_frame = Frame(procedure.env)
        formals = procedure.formals

        

        while args != nil:
            if formals == nil:
                raise SchemeError('Invalid args parsed to procedure!')
            func_frame.define(
                formals.first, scheme_eval(args.first, env))
            args = args.rest
            formals = formals.rest
        if formals != nil:
            raise SchemeError('Invalid args parsed to procedure!')
        val = scheme_eval(procedure.body.first, func_frame)
        temp = procedure.body.rest
        while temp != nil:
            val = scheme_eval(temp.first, func_frame)
            temp = temp.rest
        return val
    # END

