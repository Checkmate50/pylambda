import src.ast as ast
from src.typed_ast import *

def typecheck(program : ast.Program) -> Typed[ast.Program]:
    return Typed(program, BoolType())