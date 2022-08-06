from reprlib import recursive_repr
from scheme_classes import *
from scheme_forms import *
from scheme_eval_apply import *
from scheme_builtins import *
from scheme_reader import *
from ucb import main, trace
from copy import deepcopy

def add_builtins(frame, funcs_and_names):
    """Enter bindings in FUNCS_AND_NAMES into FRAME, an environment frame,
    as built-in procedures. Each item in FUNCS_AND_NAMES has the form
    (NAME, PYTHON-FUNCTION, INTERNAL-NAME)."""
    for name, py_func, proc_name, expect_env in funcs_and_names:
        frame.define(name, BuiltinProcedure(py_func, name=proc_name, expect_env=expect_env))

def create_global_frame():
    """Initialize and return a single-frame environment with built-in names."""
    env = Frame(None)
    env.define('eval',
               BuiltinProcedure(scheme_eval, True, 'eval'))
    env.define('apply',
               BuiltinProcedure(complete_apply, True, 'apply'))
    env.define('undefined', None)
    add_builtins(env, BUILTINS)
    return env

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


@other_builtin("lambda")
def scheme_lambda(expr_rest, env: Frame, _=None):
    formals = expr_rest.first
    body = expr_rest.rest
    if body == nil:
        raise SchemeError("Invalid lambda expressing!")
    return LambdaProcedure(formals, body, env)


@other_builtin("define")
def scheme_define(expr_rest, env: Frame, _=None):
    name = expr_rest.first
    if type(name) == Pair:
        formals = name.rest
        name = name.first
        if type(name) != str:
            raise SchemeError("Invalid defining!")
        body = expr_rest.rest
        func = LambdaProcedure(formals, body, env)
        env.define(name, func)
        func.env.define(name, func)
        return name
    if type(name) != str or name in other_builtins or builtin_find(name):
        raise SchemeError("Invalide define name " + str(name))
    value = scheme_eval(expr_rest.rest.first, env)
    env.define(name, value)
    return name


@other_builtin("eval")
def eval_in_scheme(expr_rest, env: Frame, _=None):
    return scheme_eval(scheme_eval(expr_rest.first, env), env)


@other_builtin("quote")
def scheme_quote(expr_rest, env: Frame, _=None):
    return expr_rest.first


@other_builtin("begin")
def scheme_begin(expr_rest, env: Frame, _=None):
    rt = None
    while expr_rest != nil:
        rt = scheme_eval(expr_rest.first, env, _=_)
        expr_rest = expr_rest.rest
    return rt


@other_builtin("and")
def scheme_and(expr_rest, env, _=None):
    val = True
    while expr_rest != nil:
        if expr_rest.rest == nil:
            val = scheme_eval(expr_rest.first, env, _=_)
        else:
            val = scheme_eval(expr_rest.first, env)
        if not scheme_true(val):
            return val
        expr_rest = expr_rest.rest
    return val


@other_builtin("or")
def sheme_or(expr_rest, env, _=None):
    val = False
    while expr_rest != nil:
        if expr_rest.rest == nil:
            val = scheme_eval(expr_rest.first, env, _=_)
        else:
            val = scheme_eval(expr_rest.first, env)
        if scheme_true(val):
            return val
        expr_rest = expr_rest.rest
    return val


@other_builtin("if")
def scheme_if(expr_rest, env: Frame, _=None):
    if scheme_true(scheme_eval(expr_rest.first, env)):
        return scheme_eval(expr_rest.rest.first, env, _=_)
    return scheme_eval(expr_rest.rest.rest.first, env, _=_)


@other_builtin("cond")
def scheme_cond(expr_rest, env, _=None):
    while expr_rest != nil:
        temp = expr_rest.first
        val = scheme_eval(temp.first, env, _=_)
        if scheme_true(val):
            if temp.rest == nil:
                return val
            todo = temp.rest
            while todo != nil:
                val = scheme_eval(todo.first, env, _=_)
                todo = todo.rest
            return val
        expr_rest = expr_rest.rest


@other_builtin("let")
def scheme_let(expr_rest, env, _=None):
    if _:
        let_frame = env
    else:
        let_frame = Frame(env)
    define_list = expr_rest.first
    while define_list != nil:
        pair = define_list.first
        let_frame.define(pair.first, scheme_eval(pair.rest.first, env))
        if pair.rest.rest != nil:
            raise SchemeError(
                "There should be one value to asign in let form!")
        define_list = define_list.rest

    to_eval = expr_rest.rest
    while to_eval != nil:
        val = scheme_eval(to_eval.first, let_frame, _=_)
        to_eval = to_eval.rest
    return val


@other_builtin("mu")
def scheme_mu(expr_rest, env, _=None):
    formals = expr_rest.first
    body = expr_rest.rest
    if body == nil:
        raise SchemeError("Invalid mu expressing!")
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
            if expr == "else":
                return True
            val = env.find(expr)
            if val != None:
                return val
            if builtin_find(expr):
                return "#" + expr
            else:
                raise SchemeError("Undefined name: " + str(expr))
        return expr

    operator_name = expr.first
    if type(operator_name) != str:
        if type(operator_name) == Pair:
            prcd = scheme_eval(operator_name, env, _=_)
            return scheme_apply(prcd, expr.rest, env)
        else:
            raise SchemeError("No valid operator!")

    if operator_name in other_builtins:
        return other_builtins[operator_name](expr.rest, env, _=_)

    prcd = env.find(operator_name)
    if _ and prcd == _:
        return Unevaluated(expr.rest, env)
    if prcd:
        if isinstance(prcd, Procedure):
            if _ and type(prcd) == LambdaProcedure:
                define_args(prcd, expr.rest, env, deepcopy(env))
                tail = non_tail_eval(prcd, env)
                return scheme_eval(tail.first, env, _=_)
            return scheme_apply(prcd, expr.rest, env)

    raise SchemeError("Undefined operator " + str(operator_name) + "!")
    # END Problem 1/2


def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    Frame ENV, the current environment."""
    # BEGIN Problem 1/2
    if type(procedure) == BuiltinProcedure:
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
            raise SchemeError(TypeError)
    elif type(procedure) == LambdaProcedure:
        func_frame = Frame(procedure.env)
        define_args(procedure, args, func_frame, env)
        temp = non_tail_eval(procedure, func_frame)
        return tail_eval(procedure, temp.first, func_frame)
    elif type(procedure) == MuProcedure:
        return scheme_apply(
            LambdaProcedure(procedure.formals, procedure.body, env), args, env
        )
    # END Problem 1/2


##################
# Tail Recursion #
##################

# Make classes/functions for creating tail recursive programs here!
# BEGIN Problem EC 1
def define_args(procedure, args, func_frame, env):
    """Define args in `func_frame`."""
    formals = procedure.formals
    while args != nil:
        if formals == nil:
            raise SchemeError("Invalid args parsed to procedure!")
        func_frame.define(formals.first, scheme_eval(args.first, env))
        args = args.rest
        formals = formals.rest
    if formals != nil:
        raise SchemeError("Invalid args parsed to procedure!")


def non_tail_eval(procedure, func_frame):
    """Evaluate all the exprs in `procedure` except the tail."""
    temp = procedure.body
    while temp.rest != nil:
        val = scheme_eval(temp.first, func_frame)
        temp = temp.rest
    return temp


def is_tail_call(procedure, tail, env:Frame) -> bool:
    """Check if `tail` is a tail call."""
    if type(tail) != Pair:
        return False

    if type(tail.first) == str and env.find(tail.first) == procedure:
        return True

    if type(tail.first) == Pair and tail.rest == nil:
        return is_tail_call(procedure, tail.first, env)

    if tail.first == 'if':
        return is_tail_call(procedure, tail.rest.rest.first, env) or \
            is_tail_call(procedure, tail.rest.rest.rest.first, env)

    if tail.first == 'cond':
        tail = tail.rest
        non_predict = False
        recursive = False
        global_frame = create_global_frame()
        while tail != nil:
            try:
                val = scheme_eval(tail.first.first, Frame(global_frame))
            except SchemeError:
                non_predict = True
            if is_tail_call(procedure, tail.first.rest, env):
                recursive = True
            if non_predict and recursive:
                return True
            tail = tail.rest
        return False

    tails = ['and', 'or', 'begin', 'let']
    if tail.first in tails:
        eval = False
        if tail.first == 'begin':
            env = Frame(env)
            eval = True
        while tail.rest != nil:
            tail = tail.rest
            if eval:
                scheme_eval(tail.first, env, _=procedure) 
        return is_tail_call(procedure, tail, env)

    prcd = env.find(tail.first)
    if prcd and type(prcd) == LambdaProcedure:
        body = prcd.body
        while body.rest != nil:
            body = body.rest
        return is_tail_call(procedure, body.first, env)
    
    return False


    
def tail_eval(procedure, tail, func_frame: Frame):
    """Implement tail recursion without create new frame."""
    if is_tail_call(procedure, tail, func_frame):
        unevaluated = scheme_eval(tail, func_frame, _=procedure)
        while type(unevaluated) == Unevaluated:
            define_args(procedure, unevaluated.args, unevaluated.env, deepcopy(unevaluated.env))
            unevaluated = scheme_eval(tail, unevaluated.env, _=procedure)
        return unevaluated
    return scheme_eval(tail, func_frame)

class Unevaluated:
    def __init__(self, args, env):
        self.args = args
        self.env = env
# END Problem EC 1


def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not Unevaluated.
    Right now it just calls scheme_apply, but you will need to change this
    if you attempt the extra credit."""
    validate_procedure(procedure)
    # BEGIN
    # END
