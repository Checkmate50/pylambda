import src.util

# Yes, I will manually typecheck all of these cause they're _so_ important to get right

class Expr(src.util.AbstractClass):
    pass

class Value(src.util.AbstractClass):
    pass

class Command(src.util.AbstractClass):
    pass

class Number(Value):
    def __init__(self, v : int):
        src.util.typecheck(v, int)
        self.v = v
    def __str__(self):
        return "Num " + str(self.v)

class Bool(Value):
    def __init__(self, v : bool):
        src.util.typecheck(v, bool)
        self.v = v
    def __str__(self):
        return "Bool " + str(self.v)

class Const(Expr):
    def __init__(self, v : Value):
        src.util.typecheck(v, Value)
        self.v = v
    def __str__(self):
        return "Const\n" + str(self.v)

class Op(src.util.AbstractClass):
    def __init__(self, op : str):
        src.util.typecheck(op, str)
        self.op = op
    def __str__(self):
        return self.op

class Binop(Expr):
    def __init__(self, op : Op, left : Expr, right : Expr):
        src.util.typecheck(op, Op)
        src.util.typecheck(left, Expr)
        src.util.typecheck(right, Expr)
        self.op = op
        self.left = left
        self.right = right
    def __str__(self):
        return "Binop\n" + str(self.op) + "(" + str(self.left) + ", " + str(self.right) + ")"

class Unop(Expr):
    def __init__(self, op : Op, exp : Expr):
        src.util.typecheck(op, Op)
        src.util.typecheck(exp, Expr)
        self.op = op
        self.exp = exp
    def __str__(self):
        return "Unop\n" + str(self.op) + "(" + str(self.exp) + ")"

class Skip(Command):
    def __init__(self):
        pass
    def __str__(self):
        return "Skip\n"

class Assign(Command):
    def __init__(self, var : str, exp : Expr):
        src.util.typecheck(var, str)
        src.util.typecheck(exp, Expr)
        self.var = var
        self.exp = exp        
    def __str__(self):
        return "Assign\n" + str(self.var) + "\n:=" + str(self.exp)

class Seq(Command):
    def __init__(self, c1 : Command, c2 : Command = Skip()):
        src.util.typecheck(c1, Command)
        src.util.typecheck(c2, Command)
        self.c1 = c1
        self.c2 = c2      
    def __str__(self):
        return "Seq\n" + str(self.c1) + "\n;\n" + str(self.c2)

class IfElse(Command):
    def __init__(self, b : Expr, c1 : Command, c2 : Command):
        src.util.typecheck(b, Expr)
        src.util.typecheck(c1, Command)
        src.util.typecheck(c2, Command)
        self.b = b
        self.c1 = c1
        self.c2 = c2      
    def __str__(self):
        return "If\n" + str(self.b) + "\nthen\n" + str(self.c1) + "\nelse\n" + str(self.c2)

class While(Command):
    def __init__(self, b : Expr, c : Command):
        src.util.typecheck(b, Expr)
        src.util.typecheck(c, Command)
        self.b = b
        self.c = c
    def __str__(self):
        return "While\n" + str(self.b) + "\ndo\n" + str(self.c)

class Print(Command):
    def __init__(self, exp : Expr):
        src.util.typecheck(exp, Expr)
        self.exp = exp
    def __str__(self):
        return "Print\n" + str(self.exp)

class Input(Command):
    def __init__(self, var : str):
        src.util.typecheck(var, str)
        self.var = var
    def __str__(self):
        return "Input\n" + str(self.var)

class Program:
    def __init__(self, c : Command):
        src.util.typecheck(c, Command)
        self.c = c
    def __str__(self):
        return "Program\n" + str(self.c)