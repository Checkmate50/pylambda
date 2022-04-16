import src.ast as ast
from src.util import *
from typing import List, Optional, Union

reserved = ("true", "false", "print", "input", "output", "while", "if")

# This is actually so cool
binop_precedence = [("and", "or"), ("==", "<", ">", "<=", ">="), ("+", "-"), ("*"), ("^")]

def is_lower_precedence(op1 : ast.Op, op2 = ast.Op) -> bool:
    for prec in binop_precedence:
        if op1.op in prec:
            return True # right-associative
        if op2.op in prec:
            return False
    raise InternalException(str(op1) + " is not in the precedence list")

# Dummy class for the expr stack
class OpenParen(ast.Expr):
    def __init__(self):
        pass
    def __repr__(self):
        return "OpenParen"

class ParsingException(Exception):
    def __init__(self, message : str):
        # Call the base class constructor with the parameters it needs
        super().__init__("Parsing error: " + str(message))

class ParsingExpectException(ParsingException):
    def __init__(self, expect : str, word : str):
        # Call the base class constructor with the parameters it needs
        super().__init__("expected " + str(expect) + ", got " + str(word))

class ParsingState(BaseClass):
    pass

class Lookahead(BaseClass):
    def __init__(self, lookahead):
        if not (lookahead == lookahead_binop or lookahead == lookahead_expr):
            raise InternalException("expected lookahead, got " + str(lookahead))
        self.lookahead = lookahead
    def __repr__(self):
        return "LOOKAHEAD " + str(self.unpack.__name__)

class PartialASTElement(BaseClass):
    def __init__(self, cmd : ast.Command, args : List[BaseClass]):
        self.cmd = cmd
        self.args = args
        self.index = -1

    def index_check(self, fun : str):
        if not isinstance(self.args[self.index], PartialASTElement):
                raise InternalException("Attempting to " + str(fun) + " on non-Partial element " + 
                str(self.args[self.index]) + " at index " + str(self.index))

    def set_index(self, arg : BaseClass):
        # Ok, this is _super_ janky, but control flow for command appending is done here
        if self.cmd == ast.Seq:
            self.index = 1
        if isinstance(arg, PartialExpression):
            self.index = len(self.args)-1

    def append(self, arg : BaseClass):
        if self.index == -1:
            self.args.append(arg)
            self.set_index(arg)
        else:
            self.index_check("append")
            self.args[self.index].append(arg) # Wow, that's a lotta recursion

    def overwrite(self, arg : BaseClass):
        if self.index == -1:
            if self.cmd == ast.Binop:
                self.args[-1] = arg
                self.args.pop(-2)
            else:
                self.args = [arg]
            self.set_index(arg)
        else:
            self.index_check("overwrite")
            self.args[self.index].overwrite(arg)
        
    def latest(self):
        if self.index == -1:
            if self.cmd == ast.Binop:
                return self.args[-2:]
            return self.args
        self.index_check("use latest")
        return self.args[self.index].latest()

    def pack_next(self):
        if self.index == -1:
            raise InternalException("Attempting to pack internal of unindexed partial element " + str(self))
        self.index_check("pack_next")
        self.args[self.index].pack()
        self.index += 1

    def pack(self):
        try:
            packed = [arg.pack() if isinstance(arg, PartialASTElement) else arg for arg in self.args]
            return self.cmd(*packed)
        except TypeError:
            raise ParsingException("wrong number of arguments to " + 
                str(self.cmd.__name__) + " (" + str(len(self.args)) + " given)")

    def is_partial(self):
        return isinstance(self.cmd, PartialASTElement)

class PartialCommand(PartialASTElement):
    def __repr__(self):
        return "PARTIAL_COMMAND " + str(self.cmd) + " " + str(self.args) + " " + str(self.index)

class PartialExpression(PartialASTElement):
    def __repr__(self):
        return "PARTIAL_EXPRESSION " + str(self.cmd) + " " + str(self.args) + " " + str(self.index)

class ParserState(BaseClass):
    def __init__(self):
        self.next = None
        self.state = None
        self.ops : List[PartialExpression] = []
        self.args : List[PartialASTElement] = []
        self.scope : List[PartialASTElement] = []
    def update(self, next):
        if not (isinstance(next, Lookahead) or callable(next)):
            raise InternalException("expected a function, got " + str(next))
        self.next = next
    
    def set_state(self, state : ParsingState):
        typecheck(state, ParsingState)
        self.state = state

    def push_op(self, cmd : PartialExpression):
        typecheck(cmd, PartialExpression)
        if not ((cmd.cmd == ast.Binop) or (cmd.cmd == ast.Unop) or cmd.cmd == OpenParen):
            raise InternalException("Expected Binop or Unop, got " + str(cmd.cmd))
        if cmd.cmd == ast.Unop or cmd.cmd == OpenParen:
            self.ops.append(cmd)
            return
        if len(self.ops) > 0 \
        and self.ops[-1].cmd != OpenParen \
        and is_lower_precedence(cmd.args[0], self.ops[-1].args[0]):
            self.pop_op()
        self.ops.append(cmd) 

    def pop_op(self):
        op = self.ops.pop()
        if op.cmd == OpenParen:
            return
        arg1 = self.pop_arg()
        if op.cmd == ast.Binop:
            # Disentangle the stack
            op.args.append(self.pop_arg())
        op.args.append(arg1)
        self.push_arg(op)

    def push_arg(self, arg : Union[PartialExpression, ast.Expr]):
        if not isinstance(arg, PartialExpression):
            typecheck(arg, ast.Expr)
        self.args.append(arg)
        if len(self.ops) > 0 and self.ops[-1].cmd == ast.Unop:
            self.pop_op() # unop arg comes after

    def pop_arg(self) -> Union[PartialExpression, ast.Expr]:
        return self.args.pop()

    def clean_ops(self, result : PartialASTElement, is_paren : bool):
        typecheck(result, PartialASTElement)
        if is_paren and not self.ops:
            raise ParsingException("Unmatched )")
        while (is_paren and not self.ops[-1].cmd == OpenParen) or (not is_paren and self.ops):
            if not is_paren and self.ops[-1].cmd == OpenParen:
                raise ParsingException("Unmatched (")
            self.pop_op()
            if is_paren and not self.ops:
                raise ParsingException("Unmatched )")
        if is_paren and self.ops[-1].cmd == OpenParen:
            self.pop_op()
        if not is_paren:
            while self.args:
                result.append(self.pop_arg())

    def scope_in(self, cmd : PartialASTElement):
        typecheck(cmd, PartialASTElement)
        self.scope.append(cmd)
    def scope_out(self) -> PartialASTElement:
        return self.scope.pop()

    def __repr__(self):
        return "STATE: " + str(self.next)

# So it's sorta weird, but these lookahead functions "manage" the control flow of the parser
def lookahead_binop(word : str, result : PartialCommand, state : ParserState):
    if word == ";":
        state.update(expect_semi)
    elif word == ")":
        state.update(expect_close_paren)
    else:
        state.update(expect_binop)

def lookahead_expr(word : str, result : PartialCommand, state : ParserState):
    if word in ("-", "not"):
        state.update(expect_unop)
    elif word == "(":
        state.update(expect_open_paren)
    else:
        state.update(expect_const)

def expect_semi(word : str, result : PartialCommand, state : ParserState) -> PartialASTElement:
    if not word == ";":
        raise InternalException("Expected ; got " + str(word))
    state.update(expect_command)
    state.clean_ops(result, False)
    return PartialCommand(ast.Seq, [result.pack()])

def expect_close_paren(word :str, result : PartialCommand, state : ParserState) -> PartialExpression:
    if not word == ")":
        raise InternalException("Expected ) got " + str(word))
    state.update(Lookahead(lookahead_binop))
    state.clean_ops(result, True)
    return result

def expect_binop(word : str, result : PartialCommand, state : ParserState) -> PartialExpression:
    if word in ("+", "-", "*", "^", "==", "<", ">", "<=", ">=", "and", "or"):
        state.update(Lookahead(lookahead_expr))
        state.push_op(PartialExpression(ast.Binop, [ast.Op(word)]))
        return result
    raise ParsingExpectException("binary operation", word)

def expect_unop(word : str, result : PartialCommand, state : ParserState) -> PartialExpression:
    if not (word == "-" or word == "not"):
        raise InternalException("Expected Unop got " + str(word))
    state.update(Lookahead(lookahead_expr))
    state.push_op(PartialExpression(ast.Unop, [(ast.Op(word))])) # we can do this cause we already did the lookahead
    return result

def expect_open_paren(word :str, result : PartialCommand, state : ParserState) -> PartialExpression:
    if not word == "(":
        raise InternalException("Expected ( got " + str(word))
    state.update(Lookahead(lookahead_expr))
    state.push_op(PartialExpression(OpenParen, []))
    return result

def expect_const(word : str, result : PartialCommand, state : ParserState) -> PartialASTElement:
    state.update(Lookahead(lookahead_binop))
    if word.isdigit():
        state.push_arg(ast.Const(ast.Number(int(word))))
    elif word == "true":
        state.push_arg(ast.Const(ast.Bool(True)))
    elif word == "false":
        state.push_arg(ast.Const(ast.Bool(False)))
    elif word in reserved:
        raise ParsingException("use of reserved keyword as variable " + word)
    elif word.isidentifier():
        state.push_arg(ast.Var(word))
    else:
        raise ParsingExpectException("constant, unary operation, or variable", word)
    return result

def expect_assign(word : str, result : PartialCommand, state : ParserState) -> PartialASTElement:
    if word != "=":
        raise ParsingExpectException("=", word)
    state.update(Lookahead(lookahead_expr))
    return result # No append, just looking stuff up

def expect_var(word : str, result : PartialCommand, state : ParserState) -> PartialASTElement:
    if word in reserved:
        raise ParsingException("use of reserved keyword as variable " + word)
    if not word.isidentifier():
        raise ParsingExpectException("variable", word)
    state.update(expect_semi)
    result.append(ast.Var(word))
    return result

def expect_command(word : str, result : Optional[PartialCommand], state : ParserState) -> PartialCommand:
    if word == "skip":
        state.update(expect_semi)
        cmd = PartialCommand(ast.Skip, [])
    elif word == "print":
        state.update(Lookahead(lookahead_expr))
        cmd = PartialCommand(ast.Print, [])
    elif word == "input":
        state.update(expect_var)
        cmd = PartialCommand(ast.Input, [])
    elif word in reserved:
        raise ParsingException("attempting to assign to reserved keyword " + str(word))
    elif word.isidentifier():
        state.update(expect_assign)
        cmd = PartialCommand(ast.Assign, [ast.Var(word)])
    else:
        raise ParsingExpectException("a command" + word)
    if result is None:
        return cmd
    result.append(cmd)
    return result
    
def parse_line(line : List[str], 
  result : Optional[PartialCommand], 
  state : ParserState) -> Optional[PartialCommand]:
    while line:
        if line[0].startswith("//"): #Comments 
            return result
        word = line[0]
        if result is None:
            result = expect_command(word, None, state)
            line.pop(0)
        elif isinstance(state.next, Lookahead):
            state.next.lookahead(word, result, state)
        else:
            result = state.next(word, result, state)
            line.pop(0)
    return result

def parse(line : str, 
  result : Optional[PartialCommand], 
  state : ParserState) -> Optional[PartialCommand]:
    line = line.strip() # who needs whitespace anyway
    # "Lex" the line -- yes, this is janky, yes I'm too lazy to fix it
    tokens = ";=+-*^()<>"
    for token in tokens:
        line = line.replace(token, f" {token} ")
    # Special 2-character symbols
    line = line.replace("=  =", "==") # yes, this is dumb, but it works, ok?
    line = line.replace(">  =", ">=")
    line = line.replace("<  =", "<=")
    line = line.split()
    return parse_line(line, result, state)

def parse_file(filename : str) -> ast.Program:
    result = None
    state = ParserState()
    with open(filename, 'r') as f:
        for line in f:
            result = parse(line, result, state)
    if result is None:
        return ast.Program(ast.Skip)  # default program
    try:
        result = result.pack()
    except:
        raise ParsingException("incomplete final command " + str(result.cmd.__name__))
    return ast.Program(result)