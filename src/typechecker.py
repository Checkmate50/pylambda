from src.util import *
import src.ast as ast
from src.typed_ast import *
from typing import Dict, TypeVar, Optional, Union

class TypeException(Exception):
    def __init__(self, message : str, context):
        super().__init__("Type Error on line " + str(context.line_number) + ": " + str(message))

class TypeExpectException(Exception):
    def __init__(self, expect : BaseType, word : BaseType, context):
        # Call the base class constructor with the parameters it needs
        super().__init__("expected " + str(expect) + ", got " + str(word), context)

class TypeContext(BaseClass):
    def __init__(self):
        self.vars : Dict[str, BaseType] = dict()
        self.line_number = 0

    def get_var(self, x : str) -> BaseType:
        typecheck(x, str)
        if x not in self.vars:
            TypeException("undefined variable " + str(x), self)
        return self.vars[x]

    def add_var(self, x : str, t : BaseType):
        typecheck(x, str)
        typecheck(t, BaseType)
        self.vars[x] = t

def check_statement(statement : ast.Statement, context : TypeContext) -> Typed[ast.Statement]:
    if isinstance(statement, ast.Skip):
        return Typed(statement, BoolType())

def typecheck(program : ast.Program) -> Typed[ast.Program]:
    return Typed(ast.Program(check_statement(program.s, TypeContext())), UnitType())