import src.ast as ast
from src.util import *
from src.typed_ast import Typed, IntType, BoolType, UnitType, BaseType
from typing import TypeVar, Union
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

def emit_assign(statement : Typed[ast.Assign], context : EmitContext):
    var = check_typed(statement.element.var)
    exp = check_typed(statement.element.exp)
    if var.element.v in internal_consts:
        raise Exception("Compile-time error: use of reserved name " + var.element.v)
    print(f"{var.element.v} = {string_of_expr(exp, context)}",end="")

def emit_seq(statement : ast.Seq, context : EmitContext):
    s1 = check_typed(statement.s1)
    s2 = check_typed(statement.s2)
    emit_statement(s1, context)
    print()
    emit_statement(s2, context)

def emit_if(statement : ast.If, context : EmitContext):
    raise UnimplementedException(statement)

def emit_elif(statement : ast.Elif, context : EmitContext):
    raise UnimplementedException(statement)

def emit_else(statement : ast.Else, context : EmitContext):
    raise UnimplementedException(statement)

def emit_while(statement : ast.While, context : EmitContext):
    raise UnimplementedException(statement)

def emit_print(statement : ast.Print, context : EmitContext):
    exp = check_typed(statement.exp)
    result = string_of_expr(exp, context)
    if context.debug():
        print_assignment("_value", result, context)
        print()
        result = "_value"
    if context.cli.contains("raw"):
        print("_func = ", end="")
    else:
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
        print_assignment(var.element.v, "input()", context)

def emit_statement(statement : Typed[ast.Statement], context : EmitContext):
    if isinstance(statement.element, ast.Skip):
        return
    if isinstance(statement.element, ast.Assign):
        emit_assign(statement, context)
    elif isinstance(statement.element, ast.Assign):
        emit_assign(statement.element, context)
    elif isinstance(statement.element, ast.Seq):
        emit_seq(statement.element, context)
    elif isinstance(statement.element, ast.If):
        emit_else(statement.element, context)
    elif isinstance(statement.element, ast.Elif):
        emit_elif(statement.element, context)
    elif isinstance(statement.element, ast.Else):
        emit_else(statement.element, context)
    elif isinstance(statement.element, ast.While):
        emit_while(statement.element, context)
    elif isinstance(statement.element, ast.Print):
        emit_print(statement.element, context)
    elif isinstance(statement.element, ast.Input):
        emit_input(statement.element, context)
    else:
        raise InternalException("Unimplemented statement " + str(statement))

def emit(program : Typed[ast.Program], cli : CLI):
    context = EmitContext(cli)
    print("def _raise(x): raise x # stupid lambdas and stupid statements")
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