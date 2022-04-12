from struct import unpack
import src.ast
from src.util import *
from typing import List, Optional

reserved = ("true", "false", "print", "input", "output", "while", "if")

class ParsingException(Exception):
    def __init__(self, message : str):
        # Call the base class constructor with the parameters it needs
        super().__init__("Parsing error: " + str(message))

class ParsingExpectException(ParsingException):
    def __init__(self, expect : str, word : str):
        # Call the base class constructor with the parameters it needs
        super().__init__("expected " + str(expect) + ", got " + str(word))

class ParsingState(AbstractClass):
    pass

class Lookahead(AbstractClass):
    def __init__(self, lookahead):
        if not (lookahead == lookahead_binop or lookahead == lookahead_expr):
            raise InternalException("expected lookahead, got " + str(lookahead))
        self.lookahead = lookahead
    def __str__(self):
        return "LOOKAHEAD " + str(self.unpack.__name__)

class PartialASTElement(AbstractClass):
    def __init__(self, cmd : src.ast.Command, args : List[AbstractClass]):
        self.cmd = cmd
        self.args = args
        self.index = -1
    def append(self, arg : AbstractClass):
        if self.index == -1:
            self.args.append(arg)
            # Ok, this is _super_ janky, but control flow for command appending is done here
            if self.cmd == src.ast.Seq:
                self.index = 1
        else:
            self.args[self.index].append(arg) # Wow, that's a lotta recursion
    def unpack(self):
        try:
            unpacked = [arg.unpack() if isinstance(arg, PartialCommand) else arg for arg in self.args]
            return self.cmd(*unpacked)
        except TypeError:
            raise ParsingException("wrong number of arguments to " + 
                str(self.cmd.__name__) + " (" + str(len(self.args)) + " given)")
    def is_partial(self):
        return isinstance(self.cmd, PartialCommand)

class PartialCommand(PartialASTElement):
    def __str__(self):
        return "PARTIAL_COMMAND " + str(self.cmd) + " " + str(self.args)

class PartialExpression(PartialASTElement):
    def __str__(self):
        return "PARTIAL_EXPRESSION " + str(self.cmd) + " " + str(self.args)

class ParserState(AbstractClass):
    def __init__(self):
        self.next = None
        self.scope = []
        self.state = None
    def update(self, next):
        if not (isinstance(next, Lookahead) or callable(next)):
            raise InternalException("expected a function, got " + str(next))
        self.next = next
    def scope_in(self, cmd : PartialCommand):
        self.scope.append(cmd)
    def scope_out(self) -> PartialCommand:
        return self.scope.pop()
    def set_state(self, state : ParsingState):
        typecheck(state, ParsingState)
        self.state = state
    def __str__(self):
        return "STATE: " + str(self.next)

# So it's sorta weird, but these lookahead functions "manage" the control flow of the parser
def lookahead_binop(word : str, result : PartialCommand, state : ParserState):
    if word == ";":
        state.update(expect_semi)
    else:
        state.update(expect_binop)

def lookahead_expr(word : str, result : PartialCommand, state : ParserState):
    if word in ("-", "not"):
        state.update(expect_unop)
    else:
        state.update(expect_const)

# Must follow from lookahead_semi
def expect_semi(word : str, result : PartialCommand, state : ParserState) -> PartialASTElement:
    state.update(expect_command)
    return PartialCommand(src.ast.Seq, [result.unpack()])

def expect_binop(word : str, result : PartialCommand, state : ParserState) -> PartialExpression:
    if word in ("+", "-", "*", "^", "==", "<", ">", "<=", ">=", "and", "or"):
        state.update(Lookahead(lookahead_expr))
        result.append(src.ast.Op(word))
    else:
        raise ParsingExpectException("binary operation", word)
    return result

def expect_const(word : str, result : PartialCommand, state : ParserState) -> PartialASTElement:
    state.update(Lookahead(lookahead_binop))
    if word.isdigit():
        result.append(src.ast.Const(src.ast.Number(int(word))))
    elif word == "true":
        result.append(src.ast.Const(src.ast.Bool(True)))
    elif word == "false":
        result.append(src.ast.Const(src.ast.Bool(False)))
    elif word in reserved:
        raise ParsingException("use of reserved keyword as variable " + word)
    elif word.isidentifier():
        result.append(src.ast.Var(word))
    else:
        raise ParsingExpectException("constant, unary operation, or variable", word)
    return result

# Must follow from lookahead_unop
def expect_unop(word : str, result : PartialCommand, state : ParserState) -> PartialASTElement:
    state.update(Lookahead(lookahead_expr))
    result.append(src.ast.Op(word)) # we can do this cause we already did the lookahead
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
    result.append(src.ast.Var(word))
    return result

def expect_command(word : str, result : Optional[PartialCommand], state : ParserState) -> PartialCommand:
    if word == "skip":
        state.update(expect_semi)
        cmd = PartialCommand(src.ast.Skip, [])
    elif word == "print":
        state.update(Lookahead(lookahead_expr))
        cmd = PartialCommand(src.ast.Print, [])
    elif word == "input":
        state.update(expect_var)
        cmd = PartialCommand(src.ast.Input, [])
    elif word in reserved:
        raise ParsingException("attempting to assign to reserved keyword " + str(word))
    elif word.isidentifier():
        state.update(expect_assign)
        cmd = PartialCommand(src.ast.Assign, [src.ast.Var(word)])
    else:
        raise ParsingExpectException("a command" + word)
    if result is None:
        return cmd
    result.append(cmd)
    return result
    
def parse_line(line : List[str], 
  result : Optional[PartialCommand], 
  state : ParserState) -> Optional[PartialCommand]:
    if len(line) == 0:
        return result
    if line[0].startswith("//"): #Comments 
        return result
    word = line[0]
    nxt = line[1:]
    if result is None:
        comm = expect_command(word, None, state)
        return parse_line(nxt, comm, state)
    if isinstance(state.next, Lookahead):
        state.next.lookahead(word, result, state)
        return parse_line(line, result, state)
    result = state.next(word, result, state)
    return parse_line(nxt, result, state)

def parse(line : str, 
  result : Optional[PartialCommand], 
  state : ParserState) -> Optional[PartialCommand]:
    line = line.strip() # who needs whitespace anyway
    tokens = ";=+-*^"
    for token in tokens:
        line = line.replace(token, f" {token} ")
    line = line.split()
    return parse_line(line, result, state)

def parse_file(filename : str) -> src.ast.Program:
    result = None
    state = ParserState()
    with open(filename, 'r') as f:
        for line in f:
            result = parse(line, result, state)
    if result is None:
        return src.ast.Program(src.ast.Skip)  # default program
    try:
        result = result.unpack()
    except:
        raise ParsingException("incomplete final command " + str(result.cmd.__name__))
    return src.ast.Program(result)