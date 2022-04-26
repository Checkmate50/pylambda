import src.ast as ast
from src.util import *
from src.typed_ast import Typed, IntType, BoolType, UnitType, BaseType
from typing import TypeVar, Union, Optional
from src.lc_constants import *

internal_consts = []

T = TypeVar('T')

def check_typed(term : Union[BaseClass, Typed[T]]) -> Typed[T]:
    typecheck(term, Typed)
    return term

def print_assignment(var : str, value : str, context : EmitContext):
    print(f"{var} = {value}", end="")

def interpret_bool(b : str, context : EmitContext):
    if context.cli.contains("raw"):
        print(f"{b}", end="")
    else:
        print(f"{b} (True) (False)", end="")

def int_element_str(i : str, op : str, context : EmitContext):
    return f"({op(i, context)} (lambda x : x + 1) (0))"

def interpret_int(i : str, context : EmitContext):
    if context.cli.contains("raw"):
        print(f"{i}", end="")
    else:
        print(int_element_str(i, first, context) + " - " + int_element_str(i, second, context), end="")

def string_of_value(val : Typed[ast.Value], context : EmitContext) -> str:
    if isinstance(val.element, ast.Number):
        num = bin(val.element.v)[2:]
        result = zero(context)
        while len(num) > 0:
            next = result if result == zero(context) else mult(result, two(context), context)
            result = succ(next, context) if num[0] == "1" else next
            num = num[1:]
        return f"{result}"
    if isinstance(val.element, ast.Bool):
        return f"{true(context) if val.element.v else false(context)}"
    raise InternalException("Unknown value " + str(val))

def string_of_unop(exp : Typed[ast.Unop], context : EmitContext) -> str:
    val = check_typed(exp.element.exp)
    val = string_of_expr(val, context)
    if exp.element.op.op == "-":
        return neg(val, context)
    if exp.element.op.op == "not":
        return lnot(val, context)

def string_of_binop(exp : Typed[ast.Binop], context : EmitContext) -> str:
    left = check_typed(exp.element.left)
    right = check_typed(exp.element.right)
    left = string_of_expr(left, context)
    right = string_of_expr(right, context)
    if exp.element.op.op == "+":
        return plus(left, right, context)
    if exp.element.op.op == "-":
        return minus(left, right, context)
    if exp.element.op.op == "*":
        return mult(left, right, context)
    if exp.element.op.op == "/":
        return div(left, right, context)
    if exp.element.op.op == "%":
        return mod(left, right, context)
    if exp.element.op.op == "^":
        return exponent(left, right, context)
    if exp.element.op.op == "and":
        return land(left, right, context)
    if exp.element.op.op == "or":
        return lor(left, right, context)
    if exp.element.op.op == "==":
        return eq(left, right, context)
    if exp.element.op.op == "<":
        return lt(left, right, context)
    if exp.element.op.op == ">":
        return gt(left, right, context)
    if exp.element.op.op == "<=":
        return leq(left, right, context)
    if exp.element.op.op == ">=":
        return geq(left, right, context)
    raise InternalException("unknown op " + str(exp.element.op))

def string_of_expr(exp : Typed[ast.Expr], context : EmitContext) -> str:
    if isinstance(exp.element, ast.Const):
        return string_of_value(check_typed(exp.element.v), context)
    if isinstance(exp.element, ast.Var):
        return exp.element.v
    if isinstance(exp.element, ast.Unop):
        return string_of_unop(exp, context)
    if isinstance(exp.element, ast.Binop):
        return string_of_binop(exp, context)

def str_of_vars(context : EmitContext) -> str:
    return f"({', '.join(context.vars)})"

def emit_control_function(statement : Typed[ast.Statement], context : EmitContext) -> str:
    print("  "*context.scope,end='')
    fn_name = f"_{context.fn_count}"
    args = str_of_vars(context)
    print(f"def {fn_name+args}:")
    emit_statement(statement, context.copy()) # increments scope by one
    context.fn_count += 1
    return fn_name

def emit_assign(statement : Typed[ast.Assign], context : EmitContext):
    var = check_typed(statement.element.var)
    exp = check_typed(statement.element.exp)
    print("  "*context.scope,end='')
    if var.element.v in internal_consts:
        raise Exception("Compile-time error: use of reserved name " + var.element.v)
    if var.element.v in context.vars:
        print(f"{var.element.v}.val = {string_of_expr(exp, context)}",end="")
    else:
        context.vars.append(var.element.v)
        print(f"{var.element.v} = _Var({string_of_expr(exp, context)})",end="")

def emit_seq(statement : ast.Seq, context : EmitContext):
    s1 = check_typed(statement.s1)
    s2 = check_typed(statement.s2)
    emit_statement(s1, context, s2)
    if not isinstance(s1.element, ast.Elif) and not isinstance(s1.element, ast.Else):
        print()
    emit_statement(s2, context)

def get_chain(current : Optional[Typed[ast.Statement]], context : EmitContext, follows : Optional[Typed[ast.Statement]] = None) -> str:
    if current is None:
        return 'lambda:()'
    if isinstance(current.element, ast.Seq):
        return f"{get_chain(current.element.s1, context, current.element.s2)}"
    elif isinstance(current.element, ast.Else):
        s = check_typed(current.element.s)
        fn_name = emit_control_function(s, context)
        args = str_of_vars(context)
        return f'lambda:'+fn_name+args
    elif isinstance(current.element, ast.Elif):
        s = check_typed(current.element.s)
        b = check_typed(current.element.b)
        fn_name = emit_control_function(s, context)
        args = str_of_vars(context)
        return f"{lif(string_of_expr(b, context), 'lambda:'+fn_name+args, get_chain(follows, context), context)}"
    return 'lambda:()'

def emit_if_chain(statement : ast.If, follows : Optional[Typed[ast.Statement]], context : EmitContext):
    s = check_typed(statement.s)
    b = check_typed(statement.b)
    fn_name = emit_control_function(s, context)
    chain = get_chain(follows, context)
    print("  "*context.scope,end='')
    args = str_of_vars(context)
    print(f"({lif(string_of_expr(b, context), 'lambda:'+fn_name+args, chain, context)})()",end='')

def emit_while(statement : ast.While, context : EmitContext):
    s = check_typed(statement.s)
    b = check_typed(statement.b)
    fn_name = emit_control_function(s, context)
    print("  "*context.scope,end='')
    print(f"_dummy={false(context)}") # do this for argument passing reasons
    print("  "*context.scope,end='')
    args = str_of_vars(context)
    inner_lif = lif(string_of_expr(b, context), 'lambda:_rec('+fn_name+args+')', 'lambda:()', context)
    # ok, this is super evil, but we can actually recurse in this way cause Python is _greedy_
    print(f"({z('lambda _rec: lambda _: (' + inner_lif + ')()', context)})(_dummy)")

def emit_print(statement : ast.Print, context : EmitContext):
    exp = check_typed(statement.exp)
    result = string_of_expr(exp, context)
    if context.debug():
        print("  "*context.scope,end='')
        print_assignment("_value", result, context)
        print()
        result = "_value"
    if context.cli.contains("raw"):
        print("  "*context.scope,end='')
        print("_func = ", end="")
    else:
        print("  "*context.scope,end='')
        print("print(", end="")
    if isinstance(exp.typ, BoolType):
        interpret_bool(result, context)
    elif isinstance(exp.typ, IntType):
        interpret_int(result, context)
    elif isinstance(exp.typ, UnitType):
        print("()",end="")
    else:
        raise UnimplementedException(statement)
    if context.cli.contains("raw"):
        print("\nprint(LambdaInspect()(_func).resolve(set(), set()).output(set()))", end="")
    else:
        print(")", end="")

def emit_input(statement : ast.Input, context : EmitContext):
    var = check_typed(statement.var)
    if var.element.v in internal_consts:
        raise Exception("Compile-time error: use of reserved name " + var.element.v)
    if context.no_input():
        print_assignment(var.element.v, zero(context), context)
    else:
        if context.debug():
            print("# Ugh, we have to use actual Python to interpret this thing?  How annoying")
        inp_bin = "bin(int(input()))[2:]"
        mul = mult('_rec(_bin[:-1])', two(context), context)
        check_zero = f'{mul} if _bin[-1] == "0" else {succ(mul, context)}'
        nxt_value = f"{check_zero}"
        rec = f"lambda _rec : lambda _bin : (({nxt_value}) if _bin else {zero(context)})"
        expr = f"({z(rec, context)})({inp_bin})"
        print_assignment(var.element.v, expr, context)

def emit_statement(statement : Typed[ast.Statement], context : EmitContext, follows : Optional[Typed[ast.Statement]] = None):
    if isinstance(statement.element, ast.Skip):
        print()
        return
    if isinstance(statement.element, ast.Assign):
        emit_assign(statement, context)
    elif isinstance(statement.element, ast.Assign):
        emit_assign(statement.element, context)
    elif isinstance(statement.element, ast.Seq):
        emit_seq(statement.element, context)
    elif isinstance(statement.element, ast.If):
        emit_if_chain(statement.element, follows, context)
    elif isinstance(statement.element, ast.Elif) or isinstance(statement.element, ast.Else):
        pass # Already emitted by the original `if` statement
    elif isinstance(statement.element, ast.While):
        emit_while(statement.element, context)
    elif isinstance(statement.element, ast.Print):
        emit_print(statement.element, context)
    elif isinstance(statement.element, ast.Input):
        emit_input(statement.element, context)
    else:
        raise InternalException("Unimplemented statement " + str(statement))

import sys
def emit(program : Typed[ast.Program], cli : CLI):
    context = EmitContext(cli)
    print("import sys")
    print("sys.setrecursionlimit(100000) # This is fine, nothing can possibly go wrong")
    print("def _raise(x): raise x # stupid lambdas and stupid statements")
    print(scope_manager)
    if context.raw():
        print(lc_inspector)
    if context.debug():
        for c in functions_to_write:
            # Get c(context)[1:-2] to clean up unneeded parens
            s = c(context)
            if not s.startswith("("):
                raise InternalException("Badly formatted definition function " + s)
            s = s[1:-1]
            internal_consts.append(f"{retrieve_name_constant(c)[0].upper().split('_')[0]}")
            print_assignment(internal_consts[-1], s, context)
            print()
    context.interp = True
    emit_statement(check_typed(program.element.s), context)