import src.util as util
from typing import Optional

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

class Const(Expr):
    def __init__(self, v : Value):
        util.typecheck(v, Value)
        self.v = v
    def __repr__(self):
        return "Const " + str(self.v)

class Op(util.BaseClass):
    def __init__(self, op : str):
        util.typecheck(op, str)
        self.op = op
    def __repr__(self):
        return "Op " + str(self.op)

class Var(Expr):
    def __init__(self, v : str):
        util.typecheck(v, str)
        self.v = v
    def __repr__(self):
        return "Var " + str(self.v)

class Binop(Expr):
    def __init__(self, op : Op, left : Expr, right : Expr):
        # Note that op comes first cause of precedence stack crap
        util.typecheck(op, Op)
        util.typecheck(left, Expr)
        util.typecheck(right, Expr)
        self.op = op
        self.left = left
        self.right = right
    def __repr__(self):
        return "Binop " + str(self.op) + "(" + str(self.left) + ", " + str(self.right) + ")"

class Unop(Expr):
    def __init__(self, op : Op, exp : Expr):
        util.typecheck(op, Op)
        util.typecheck(exp, Expr)
        self.op = op
        self.exp = exp
    def __repr__(self):
        return "Unop " + str(self.op) + "(" + str(self.exp) + ")"

class Skip(Statement):
    def __init__(self, ln : int):
        util.typecheck(ln, int)
        self.ln = ln
    def __repr__(self):
        return "Skip\n"

class Assign(Statement):
    def __init__(self, ln : int, var : Var, exp : Expr):
        util.typecheck(ln, int)
        util.typecheck(var, Var)
        util.typecheck(exp, Expr)
        
        self.ln = ln
        self.var = var
        self.exp = exp
    def __repr__(self):
        return "Assign\n" + str(self.var) + "\n=\n" + str(self.exp)

class Seq(Statement):
    def __init__(self, ln : int, c1 : Statement, c2 : Statement = Skip()):
        util.typecheck(ln, int)
        util.typecheck(c1, Statement)
        util.typecheck(c2, Statement)

        self.ln = ln
        self.c1 = c1
        self.c2 = c2
    def __repr__(self):
        return str(self.c1) + "\n;\n" + str(self.c2)

class If(Statement):
    def __init__(self, ln : int, b : Expr, c : Statement, e : Statement = Skip()):
        util.typecheck(ln, int)
        util.typecheck(b, Expr)
        util.typecheck(c, Statement)
        util.typecheck(e, Statement)
        
        self.ln = ln
        self.b = b
        self.c = c
        self.e = e
    def __repr__(self):
        return "If\n" + str(self.b) + "\n{\n" + str(self.c) + "\n}\n"

class Else(Statement):
    def __init__(self, ln : int, c : Statement):
        util.typecheck(ln, int)
        util.typecheck(c, Statement)
        
        self.ln = ln
        self.c = c
    def __repr__(self):
        return "If\n" + str(self.b) + "\n{\n" + str(self.c) + "\n}\n"

class While(Statement):
    def __init__(self, ln : int, b : Expr, c : Statement):
        util.typecheck(ln, int)
        util.typecheck(b, Expr)
        util.typecheck(c, Statement)

        self.ln = ln
        self.b = b
        self.c = c
    def __repr__(self):
        return "While\n" + str(self.b) + "\n{\n" + str(self.c) + "\n}\n"

class Print(Statement):
    def __init__(self, ln : int, exp : Expr):
        util.typecheck(ln, int)
        util.typecheck(exp, Expr)
        
        self.ln = ln
        self.exp = exp
    def __repr__(self):
        return "Print\n" + str(self.exp)

class Input(Statement):
    def __init__(self, ln : int, var : Var):
        util.typecheck(ln, int)
        util.typecheck(var, Var)
        
        self.ln = ln
        self.var = var
    def __repr__(self):
        return "Input\n" + str(self.var)

class Program:
    def __init__(self, c : Statement):
        util.typecheck(c, Statement)
        self.c = c
    def __repr__(self):
        return "Program\n" + str(self.c)