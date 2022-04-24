from src.util import *
import src.ast as ast
from src.typed_ast import *
from typing import Dict, Tuple, Union, Type

class TypeException(Exception):
    def __init__(self, message : str, context):
        super().__init__("Type Error on line " + str(context.line_number) + ": " + str(message))

class TypeExpectException(TypeException):
    def __init__(self, expect : BaseType, word : BaseType, context):
        super().__init__("expected " + str(expect) + ", got " + str(word), context)

class TypeContext(BaseClass):
    def __init__(self):
        self.vars : Dict[str, BaseType] = dict()
        self.line_number = 0

    def get_var(self, x : str) -> BaseType:
        typecheck(x, str)
        if x not in self.vars:
            raise TypeException("undefined variable " + str(x), self)
        return self.vars[x]

    def add_var(self, x : str, t : BaseType):
        typecheck(x, str)
        typecheck(t, BaseType)
        self.vars[x] = t

    def copy(self):
        result = TypeContext()
        result.vars = self.vars.copy()
        return result

    def __repr__(self):
        return "TYPE_CONTEXT " + str(self.line_number) + "\n" + str(self.vars)

def check_const(c : ast.Const, context : TypeContext) -> Typed[ast.Const]:
    if isinstance(c.v, ast.Bool):
        c.v = Typed(c.v, BoolType())
        return Typed(c, BoolType())
    if isinstance(c.v, ast.Number):
        c.v = Typed(c.v, IntType())
        return Typed(c, IntType())
    raise InternalException("Unknown matched const " + str(c))

def check_var(var : Union[ast.Var, Typed], context : TypeContext) -> Typed[str]:
    if isinstance(var, Typed):
        raise InternalException("Unexpected Typed var " + str(var))
    if isinstance(var.v, Typed):
        raise InternalException("Unexpected Typed v in" + str(var))
    return Typed(var, context.get_var(var.v))

def match_unop(to_check : Tuple[str, BaseType], expect : Tuple[str, Type[BaseType]], context) -> bool:
    if to_check[0] != expect[0]:
        return False
    if not isinstance(to_check[1], expect[1]):
        raise TypeExpectException(expect[1](), to_check[1], context)
    return True

def match_binop(to_check : Tuple[str, BaseType, BaseType], expect : Tuple[List[str], Type[BaseType], Type[BaseType]], context) -> bool:
    if to_check[0] not in expect[0]:
        return False
    if not isinstance(to_check[1], expect[1]):
        raise TypeExpectException(expect[1](), to_check[1], context)
    if not isinstance(to_check[2], expect[2]):
        raise TypeExpectException(expect[2](), to_check[2], context)
    return True

def match_binop_any(to_check : Tuple[str, BaseType, BaseType], expect : Tuple[List[str], List[BaseType], List[BaseType]], context) -> bool:
    if to_check[0] not in expect[0]:
        return False
    if len(expect[1]) != len(expect[2]):
        raise InternalException("Invalid pair of expect lists " + str(expect[1]) + " and " + str(expect[2]))
    for t1, t2 in zip(expect[1], expect[2]):
        if isinstance(to_check[1], t1) and isinstance(to_check[2], t2):
            return True
    raise TypeExpectException([(x[0](), x[1]()) for x in zip(expect[1], expect[2])], (to_check[1], to_check[2]), context)

def check_unop(u : ast.Unop, context : TypeContext) -> Typed[ast.Unop]:
    u.exp = check_expr(u.exp, context)
    check = (u.op.op, u.exp.typ)
    if match_unop(check, ("-", IntType), context):
        return Typed(u, IntType())
    if match_unop(check, ("not", BoolType), context):
        return Typed(u, BoolType())
    raise InternalException("Unknown unary operation " + str(u.op.op))

def check_binop(b : ast.Binop, context : TypeContext) -> Typed[ast.Binop]:
    b.left = check_expr(b.left, context)
    b.right = check_expr(b.right, context)
    check = (b.op.op, b.left.typ, b.right.typ)
    if match_binop(check, (["+", "-", "*", "%", "/", "^"], IntType, IntType), context):
        return Typed(b, IntType())
    if match_binop(check, (["<", ">", "<=", ">="], IntType, IntType), context):
        return Typed(b, BoolType())
    if match_binop_any(check, (["=="], [BoolType, IntType], [BoolType, IntType]), context):
        return Typed(b, BoolType())
    if match_binop(check, (["and", "or"], BoolType, BoolType), context):
        return Typed(b, BoolType())
    raise InternalException("Unknown binary operation " + str(b.op.op))

def check_expr(exp : Union[ast.Expr, Typed], context : TypeContext) -> Typed[ast.Expr]:
    if isinstance(exp, ast.Const):
        return check_const(exp, context)
    if isinstance(exp, ast.Var):
        v = check_var(exp, context)
        return Typed(exp, v.typ)
    if isinstance(exp, ast.Unop):
        return check_unop(exp, context)
    if isinstance(exp, ast.Binop):
        return check_binop(exp, context)

def check_assign(statement : ast.Assign, context : TypeContext) -> Typed[ast.Assign]:
    if isinstance(statement.var, Typed) or isinstance(statement.var.v, Typed):
        raise InternalException("Unexpected typed var in " + str(statement))
    statement.exp = check_expr(statement.exp, context)
    context.add_var(statement.var.v, statement.exp.typ)
    statement.var = Typed(statement.var, statement.exp.typ)
    return Typed(statement, UnitType())

def check_seq(statement : ast.Seq, context : TypeContext) -> Typed[ast.Seq]:
    if (isinstance(statement.s2, ast.Seq) and (isinstance(statement.s2.s1, ast.Else) or isinstance(statement.s2.s1, ast.Elif))) \
        or isinstance(statement.s2, ast.Else) or isinstance(statement.s2, ast.Elif):
        if not (isinstance(statement.s1, ast.If) or isinstance(statement.s1, ast.Elif)):
            raise TypeException("Elif or Else statement without preceding if or elif statement", context)
    statement.s1 = check_statement(statement.s1, context)
    statement.s2 = check_statement(statement.s2, context)
    return Typed(statement, UnitType())

def check_if(statement : Union[ast.If, ast.Elif, ast.While], context : TypeContext) -> Typed[Union[ast.If, ast.Elif, ast.While]]:
    # We can union this whole mess cause of similar names and duck typing...
    statement.b = check_expr(statement.b, context) # this is terrible stuff
    if not isinstance(statement.b.typ, BoolType):
        raise TypeExpectException(BoolType(), statement.b.typ, context)
    statement.s = check_statement(statement.s, context.copy()) # Scope!
    return Typed(statement, UnitType())

def check_else(statement : ast.Else, context : TypeContext) -> Typed[ast.Else]:
    statement.s = check_statement(statement.s, context.copy()) # Scope!
    return Typed(statement, UnitType())

def check_print(statement : ast.Print, context : TypeContext) -> Typed[ast.Print]:
    statement.exp = check_expr(statement.exp, context)
    return Typed(statement, UnitType())

def check_input(statement : ast.Input, context : TypeContext) -> Typed[ast.Input]:
    if isinstance(statement.var, Typed) or isinstance(statement.var.v, Typed):
        raise InternalException("Unexpected typed var in " + str(statement))
    context.add_var(statement.var.v, IntType())
    statement.var = Typed(statement.var, IntType())
    return Typed(statement, UnitType())

def check_statement(statement : Union[ast.Statement, Typed], context : TypeContext) -> Typed[ast.Statement]:
    if isinstance(statement, Typed):
        raise InternalException("Unexpected typed statement", Typed)
    context.line_number = statement.ln # Typesafe cause ast.Statement is an abstract class
    if isinstance(statement, ast.Skip):
        return Typed(statement, UnitType())
    if isinstance(statement, ast.Assign):
        return check_assign(statement, context)
    if isinstance(statement, ast.Seq):
        return check_seq(statement, context)
    if isinstance(statement, ast.If):
        return check_if(statement, context)
    if isinstance(statement, ast.Elif):
        return check_if(statement, context)
    if isinstance(statement, ast.Else):
        return check_else(statement, context)
    if isinstance(statement, ast.While):
        return check_if(statement, context)
    if isinstance(statement, ast.Print):
        return check_print(statement, context)
    if isinstance(statement, ast.Input):
        return check_input(statement, context)
    raise InternalException("Unknown matched statement " + str(statement))

def typecheck_program(program : ast.Program) -> Typed[ast.Program]:
    context = TypeContext()
    handle_seq = program.s.s1 if isinstance(program.s, ast.Seq) else program.s
    if isinstance(handle_seq, ast.Elif) or isinstance(handle_seq, ast.Else):
        raise TypeException("Cannot start program with Elif or If statement", context)
    return Typed(ast.Program(check_statement(program.s, context)), UnitType())