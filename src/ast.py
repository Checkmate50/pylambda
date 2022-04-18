import src.util as util
from typing import Union
from src.typed_ast import Typed

# Yes, I will manually typecheck all of these cause they're _so_ important to get right

class Expr(util.BaseClass):
    pass

class Value(util.BaseClass):
    pass

class Statement(util.BaseClass):
    pass

class Number(Value):
    def __init__(self, v : int):
        util.typecheck(v, int)
        self.v = v
    def __repr__(self):
        return "Num " + str(self.v)

class Bool(Value):
    def __init__(self, v : bool):
        util.typecheck(v, bool)
        self.v = v
    def __repr__(self):
        return "Bool " + str(self.v)

class Op(util.BaseClass):
    def __init__(self, op : str):
        util.typecheck(op, str)
        self.op = op
    def __repr__(self):
        return "Op " + str(self.op)

class Const(Expr):
    def __init__(self, v : Union[Value, Typed[Value]]):
        util.typecheck_any(v, [Value, Typed])
        self.v = v
    def __repr__(self):
        return "Const " + str(self.v)

class Var(Expr):
    def __init__(self, v : Union[str, Typed[str]]):
        util.typecheck_any(v, [str, Typed])
        self.v = v
    def __repr__(self):
        return "Var " + str(self.v)

class Unop(Expr):
    def __init__(self, op : Op, exp : Union[Expr, Typed[Expr]]):
        util.typecheck(op, Op)
        util.typecheck_any(exp, [Expr, Typed])
        self.op = op
        self.exp = exp
    def __repr__(self):
        return "Unop " + str(self.op) + "(" + str(self.exp) + ")"

class Binop(Expr):
    def __init__(self, op : Op, left : Union[Expr, Typed[Expr]], right : Union[Expr, Typed[Expr]]):
        # Note that op comes first cause of precedence stack crap
        util.typecheck(op, Op)
        util.typecheck_any(left, [Expr, Typed])
        util.typecheck_any(right, [Expr, Typed])
        self.op = op
        self.left = left
        self.right = right
    def __repr__(self):
        return "Binop " + str(self.op) + "(" + str(self.left) + ", " + str(self.right) + ")"

class Skip(Statement):
    def __init__(self, ln : int):
        util.typecheck(ln, int)
        self.ln = ln
    def __repr__(self):
        return "Skip\n"

class Assign(Statement):
    def __init__(self, ln : int, var : Union[Var, Typed[Var]], exp : Union[Expr, Typed[Expr]]):
        util.typecheck(ln, int)
        util.typecheck_any(var, [Var, Typed])
        util.typecheck_any(exp, [Expr, Typed])
        
        self.ln = ln
        self.var = var
        self.exp = exp
    def __repr__(self):
        return "Assign\n" + str(self.var) + "\n=\n" + str(self.exp)

class Seq(Statement):
    def __init__(self, ln : int, s1 : Union[Statement, Typed[Statement]], s2 : Union[Statement, Typed[Statement]] = Skip(-1)):
        util.typecheck(ln, int)
        util.typecheck_any(s1, [Statement, Typed])
        util.typecheck_any(s2, [Statement, Typed])

        self.ln = ln
        self.s1 = s1
        self.s2 = s2
    def __repr__(self):
        return str(self.s1) + "\n;\n" + str(self.s2)

class If(Statement):
    def __init__(self, ln : int, b : Union[Expr, Typed[Expr]], s : Union[Statement, Typed[Statement]]):
        util.typecheck(ln, int)
        util.typecheck_any(b, [Expr, Typed])
        util.typecheck_any(s, [Statement, Typed])
        
        self.ln = ln
        self.b = b
        self.s = s
    def __repr__(self):
        return "If\n" + str(self.b) + "\n{\n" + str(self.s) + "}"

class Elif(Statement):
    def __init__(self, ln : int, b : Union[Expr, Typed[Expr]], s : Union[Statement, Typed[Statement]]):
        util.typecheck(ln, int)
        util.typecheck_any(b, [Expr, Typed])
        util.typecheck_any(s, [Statement, Typed])
        
        self.ln = ln
        self.b = b
        self.s = s
    def __repr__(self):
        return "Elif\n" + str(self.b) + "\n{\n" + str(self.s) + "}"

class Else(Statement):
    def __init__(self, ln : int, s : Union[Statement, Typed[Statement]]):
        util.typecheck(ln, int)
        util.typecheck_any(s, [Statement, Typed])
        
        self.ln = ln
        self.s = s
    def __repr__(self):
        return "Else" + "\n{\n" + str(self.s) + "}"

class While(Statement):
    def __init__(self, ln : int, b : Union[Expr, Typed[Expr]], s : Union[Statement, Typed[Statement]]):
        util.typecheck(ln, int)
        util.typecheck_any(b, [Expr, Typed])
        util.typecheck_any(s, [Statement, Typed])

        self.ln = ln
        self.b = b
        self.s = s
    def __repr__(self):
        return "While\n" + str(self.b) + "\n{\n" + str(self.s) + "}"

class Print(Statement):
    def __init__(self, ln : int, exp : Union[Expr, Typed[Expr]]):
        util.typecheck(ln, int)
        util.typecheck_any(exp, [Expr, Typed])
        
        self.ln = ln
        self.exp = exp
    def __repr__(self):
        return "Print\n" + str(self.exp)

class Input(Statement):
    def __init__(self, ln : int, var : Union[Var, Typed[Var]]):
        util.typecheck(ln, int)
        util.typecheck_any(var, [Var, Typed])
        
        self.ln = ln
        self.var = var
    def __repr__(self):
        return "Input\n" + str(self.var)

class Program(util.BaseClass):
    def __init__(self, s : Union[Statement, Typed[Statement]]):
        util.typecheck_any(s, [Statement, Typed])
        self.s = s
    def __repr__(self):
        return "Program\n" + str(self.s)