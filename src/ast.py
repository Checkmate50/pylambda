import src.util as util

# Yes, I will manually typecheck all of these cause they're _so_ important to get right

class Expr(util.BaseClass):
    pass

class Value(util.BaseClass):
    pass

class Command(util.BaseClass):
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

class Skip(Command):
    def __init__(self, ln : int):
        util.typecheck(ln, int)
        self.ln = ln
    def __repr__(self):
        return "Skip\n"

class Assign(Command):
    def __init__(self, ln : int, var : Var, exp : Expr):
        util.typecheck(var, Var)
        util.typecheck(exp, Expr)
        util.typecheck(ln, int)
        self.var = var
        self.exp = exp
        self.ln = ln
    def __repr__(self):
        return "Assign\n" + str(self.var) + "\n=\n" + str(self.exp)

class Seq(Command):
    def __init__(self, ln : int, c1 : Command, c2 : Command = Skip()):
        util.typecheck(c1, Command)
        util.typecheck(c2, Command)
        util.typecheck(ln, int)
        self.c1 = c1
        self.c2 = c2
        self.ln = ln
    def __repr__(self):
        return str(self.c1) + "\n;\n" + str(self.c2)

class IfElse(Command):
    def __init__(self, ln : int, b : Expr, c : Command):
        util.typecheck(b, Expr)
        util.typecheck(c, Command)
        util.typecheck(ln, int)
        self.b = b
        self.c = c
        self.ln = ln
    def __repr__(self):
        return "If\n" + str(self.b) + "\n{\n" + str(self.c) + "\n}\n"

class While(Command):
    def __init__(self, ln : int, b : Expr, c : Command):
        util.typecheck(b, Expr)
        util.typecheck(c, Command)
        util.typecheck(ln, int)
        self.b = b
        self.c = c
        self.ln = ln
    def __repr__(self):
        return "While\n" + str(self.b) + "\n{\n" + str(self.c) + "\n}\n"

class Print(Command):
    def __init__(self, ln : int, exp : Expr):
        util.typecheck(exp, Expr)
        util.typecheck(ln, int)
        self.exp = exp
        self.ln = ln
    def __repr__(self):
        return "Print\n" + str(self.exp)

class Input(Command):
    def __init__(self, ln : int, var : Var):
        util.typecheck(var, Var)
        util.typecheck(ln, int)
        self.var = var
        self.ln = ln
    def __repr__(self):
        return "Input\n" + str(self.var)

class Program:
    def __init__(self, c : Command):
        util.typecheck(c, Command)
        self.c = c
    def __repr__(self):
        return "Program\n" + str(self.c)