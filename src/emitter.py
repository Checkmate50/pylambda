import src.ast as ast
from src.util import *
from src.typed_ast import Typed, IntType, BoolType, UnitType, BaseType
from typing import TypeVar, Union, Set, List
import inspect
from copy import copy

class CLI:
    def __init__(self, args : Set[str] = set()):
        self.set_args(args)

    def set_args(self, args : List[str]):
        for i in range(len(args)):
            if not args[i].startswith("--") or len(args[i]) < 2:
                raise Exception("Invalid argument " + str(args[i]))
            args[i] = args[i][2:]
        self.args = set(args)

    def contains(self, arg : str) -> bool:
        return arg in self.args

    def __repr__(self):
        return "CLI: " + str(self.args)

class EmitContext(BaseClass):
    def __init__(self, cli : CLI):
        self.cli = cli
        self.interp : bool = False

    def raw(self):
        return self.cli.contains("raw")

    def debug(self):
        return self.cli.contains("debug")

    def __repr__(self):
        return "EMIT_CONTEXT" + str(self.cli)

T = TypeVar('T')

def check_typed(term : Union[BaseClass, Typed[T]]) -> Typed[T]:
    typecheck(term, Typed)
    return term

def retrieve_name_constant(var : any) -> List[str]:
    callers_local_vars = inspect.currentframe().f_globals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]

# maybe_debug is too long to type
def mr(val : str, context : EmitContext) -> str:
    if context.debug():
        return f"{retrieve_name_constant(val)[0].upper().split('_')[0]}"
    return f"{val(context)}"

def false(context : EmitContext) -> str:
    return "(lambda x : lambda y : y)"

def true(context : EmitContext) -> str:
    return "(lambda x : lambda y : x)"

def pair_def(context : EmitContext) -> str:
    return "(lambda x : lambda y : lambda f : (f (x) (y)))"

def first_def(context : EmitContext) -> str:
    return f"(lambda x : (x ({true(context)})))"

def second_def(context : EmitContext) -> str:
    return f"(lambda x : (x ({false(context)})))"

def pair(left : str, right : str, context : EmitContext) -> str:
    return f"{mr(pair_def, context)} ({left}) ({right})"

def first(p : str, context : EmitContext) -> str:
    return f"{mr(first_def, context)} ({p})"

def second(p : str, context : EmitContext) -> str:
    return f"{mr(second_def, context)} ({p})"

def czero(context : EmitContext) -> str:
    return "(lambda f : lambda x : x)"

# This is an _unusual_ representation
def zero(context : EmitContext) -> str:
    return f"({pair(mr(czero, context), mr(czero, context), context)})"

def csucc(context : EmitContext):
    return "(lambda n : lambda f : lambda x : (f (n (f) (x))))"

def cplus(context : EmitContext) -> str:
    return f"(lambda m : lambda n : (m ({mr(csucc, context)}) (n)))"

def cmult(context : EmitContext) -> str:
    return f"(lambda m : lambda n : lambda f : (m (n (f))))"

def cexp(context : EmitContext) -> str:
    return f"(lambda b : lambda e : e (b))"

def appfirst_def(context : EmitContext) -> str:
    return f"(lambda f : lambda p : ({pair('f ({})'.format(first('p', context)), second('p', context), context)}))"

def appfirst(f : str, v : str, context : EmitContext) -> str:
    return f"{mr(appfirst_def, context)} ({f}) ({v})"

def appsecond_def(context : EmitContext) -> str:
    return f"(lambda f : lambda p : ({pair(first('p', context), 'f ({})'.format(second('p', context)), context)}))"

def appsecond(f : str, v : str, context : EmitContext) -> str:
    return f"{mr(appsecond_def, context)} ({f}) ({v})"

def succ_def(context: EmitContext) -> str:
    return f"(lambda n : {appfirst(mr(csucc, context), 'n', context)})"

def succ(n : str, context: EmitContext) -> str:
    return f"{mr(succ_def, context)} ({n})"

def pred_def(context : EmitContext) -> str:
    return f"(lambda n : {appsecond(mr(csucc, context), 'n', context)})"

def pred(n : str, context: EmitContext) -> str:
    return f"{mr(pred_def(context), context)} ({n})"

CONSTANTS = [false, true, pair_def, first_def, second_def, 
    czero, zero, csucc, cplus, cmult, cexp, appfirst_def, appsecond_def, succ_def, pred_def]

def print_assignment(var : str, value : str, context : EmitContext):
    print(f"{var} = {value}", end="")

def interpret_bool(b : str, context : EmitContext):
    if context.cli.contains("raw"):
        print(f"{b}", end="")
    else:
        print(f"{b} (True) (False)", end="")

def int_element_str(i : str, access, op : str, context : EmitContext):
    return f"(({access(i, context)}) ({op}) (0))"

def interpret_int(i : str, context : EmitContext):
    if context.cli.contains("raw"):
        print(f"{i}", end="")
    else:
        print(int_element_str(i, first, "lambda x : x + 1", context) + 
        " + " + int_element_str(i, second, "lambda x : x - 1", context), end="")

def string_of_value(val : Typed[ast.Value], context : EmitContext) -> str:
    if isinstance(val.element, ast.Number):
        result = zero(context)
        for _ in range(val.element.v):
            result = succ(result, context)
        return f"({result})"
    if isinstance(val.element, ast.Bool):
        return f"({mr(true, context)})" if val.element.v else f"({mr(false, context)})"
    raise InternalException("Unknown value " + str(val))

def string_of_unop(exp : Typed[ast.Unop], context : EmitContext) -> str:
    raise UnimplementedException(exp)

def string_of_binop(exp : Typed[ast.Binop], context : EmitContext) -> str:
    raise UnimplementedException(exp)

def string_of_expr(exp : Typed[ast.Expr], context : EmitContext) -> str:
    if isinstance(exp.element, ast.Const):
        return string_of_value(check_typed(exp.element.v), context)
    if isinstance(exp.element, ast.Var):
        return check_typed(exp.element.v).element
    if isinstance(exp.element, ast.Unop):
        return string_of_unop(exp, context)
    if isinstance(exp.element, ast.Binop):
        return string_of_binop(exp, context)

def emit_assign(statement : ast.Assign, context : EmitContext):
    UnimplementedException(statement)

def emit_seq(statement : ast.Seq, context : EmitContext):
    s1 = check_typed(statement.s1)
    s2 = check_typed(statement.s2)
    emit_statement(s1, context)
    print()
    emit_statement(s2, context)

def emit_if(statement : ast.If, context : EmitContext):
    UnimplementedException(statement)

def emit_elif(statement : ast.Elif, context : EmitContext):
    UnimplementedException(statement)

def emit_else(statement : ast.Else, context : EmitContext):
    UnimplementedException(statement)

def emit_while(statement : ast.While, context : EmitContext):
    UnimplementedException(statement)

def emit_print(statement : ast.Print, context : EmitContext):
    exp = check_typed(statement.exp)
    result = string_of_expr(exp, context)
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
    else:
        raise UnimplementedException(statement)
    if context.cli.contains("raw"):
        print("\nprint(str(inspect.getsourcelines(_func)[0]).strip(\"['\\\\n']\").split(\" = \")[1])", end="")
    else:
        print(")", end="")

def emit_input(statement : ast.Input, context : EmitContext):
    var = check_typed(statement.var)
    print_assignment(var, "input()", context)

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
    if context.raw():
        print("import inspect\n")
    if context.debug():
        for c in CONSTANTS:
            # Get c(context)[1:-2] to clean up unneeded parens
            s = c(context)
            if not s.startswith("("):
                raise InternalException("Badly formatted definition function " + s)
            print_assignment(f"{retrieve_name_constant(c)[0].upper().split('_')[0]}", s, context)
            print()
    context.interp = True
    emit_statement(check_typed(program.element.s), context)