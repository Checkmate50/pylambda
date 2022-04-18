import src.ast as ast
from src.util import *
from src.typed_ast import Typed, IntType, BoolType, UnitType, BaseType
from typing import TypeVar, Union, Set, List

class CLI:
    def __init__(self):
        self.args : Set[str] = set()

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

    def __repr__(self):
        return "EMIT_CONTEXT" + str(self.cli)

FALSE = "lambda x : lambda y : y"
TRUE = "lambda x : lambda y : x"

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

def string_of_value(val : Typed[ast.Value], context : EmitContext) -> str:
    if isinstance(val.element, ast.Number):
        raise UnimplementedException(val)
    if isinstance(val.element, ast.Bool):
        if context.cli.contains("readable"):
            return "TRUE" if val.element.v else "FALSE"
        return f"({TRUE})" if val.element.v else f"({FALSE})"
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
    if context.cli.contains("raw"):
        print("_func = ", end="")
    else:
        print("print(", end="")
    if isinstance(exp.typ, BoolType):
        interpret_bool(string_of_expr(exp, context), context)
    elif isinstance(exp.typ, IntType):
        raise UnimplementedException(statement)
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
    if context.cli.contains("raw"):
        print("import inspect\n")
    if context.cli.contains("readable"):
        print_assignment("FALSE", FALSE, context)
        print()
        print_assignment("TRUE", TRUE, context)
        print()
    emit_statement(check_typed(program.element.s), context)