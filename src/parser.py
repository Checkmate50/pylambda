import src.ast
from src.util import *
from typing import List, Optional

class Lookahead(AbstractClass):
    def __init__(self, unpack):
        if not (unpack == lookahead_semi or unpack == lookahead_unop):
            raise Exception("Internal Error, expected lookahead, got " + str(unpack))
        self.unpack = unpack
    def __str__(self):
        return "LOOKAHEAD " + str(self.unpack.__name__)

class ParserState(AbstractClass):
    def __init__(self):
        self.next = None
    def update(self, next):
        if not (isinstance(next, Lookahead) or callable(next)):
            raise Exception("Internal Error: Expected a function, got " + str(next))
        self.next = next
    def __str__(self):
        return "STATE: " + str(self.next)

class PartialCommand(AbstractClass):
    def __init__(self, cmd : src.ast.Command, args : List[AbstractClass]):
        self.cmd = cmd
        self.args = args
    def append(self, arg : AbstractClass):
        self.args.append(arg)
    def unpack(self):
        return self.cmd(*self.args)
    def is_partial(self):
        return isinstance(self.cmd, PartialCommand)
    def __str__(self):
        return "PARTIALCOMMAND " + str(self.cmd) + " " + str(self.args)

def lookahead_semi(word : str, result : PartialCommand, state : ParserState):
    if word == ";":
        state.update(expect_semi)
    else:
        state.update(expect_binop)

def lookahead_unop(word : str, result : PartialCommand, state : ParserState):
    if word in ("-", "not"):
        state.update(expect_unop)
    else:
        state.update(expect_const)

# Must follow from lookahead_semi
def expect_semi(word : str, result : PartialCommand, state : ParserState) -> PartialCommand:
    state.update(expect_command)
    return PartialCommand(src.ast.Seq, [result.unpack()])

def expect_binop(word : str, result : PartialCommand, state : ParserState) -> PartialCommand:
    if word in ("+", "-", "*", "^", "==", "<", ">", "<=", ">=", "and", "or"):
        state.update(Lookahead(lookahead_unop))
        result.append(src.ast.Op(word))
    else:
        raise Exception("Parsing error: expected binary operation, got " + word)
    return result

def expect_const(word : str, result : PartialCommand, state : ParserState) -> PartialCommand:
    if word.isdigit():
        state.update(Lookahead(lookahead_semi))
        result.append(src.ast.Const(src.ast.Number(int(word))))
    elif word == "true":
        state.update(Lookahead(lookahead_semi))
        result.append(src.ast.Const(src.ast.Bool(True)))
    elif word == "false":
        state.update(Lookahead(lookahead_semi))
        result.append(src.ast.Const(src.ast.Bool(False)))
    else:
        raise Exception("Parsing error: expected constant or unary operation, got " + word)
    return result

# Must follow from lookahead_unop
def expect_unop(word : str, result : PartialCommand, state : ParserState):
    state.update(Lookahead(lookahead_unop))
    result.append(src.ast.Op(word)) # we can do this cause we already did the lookahead
    return result

def expect_command(word : str, result : PartialCommand, state : ParserState) -> PartialCommand:
    if word == "skip":
        state.update(expect_semi)
        return PartialCommand(src.ast.Skip, [])
    if word == "print":
        state.update(Lookahead(lookahead_unop))
        return PartialCommand(src.ast.Print, [])
    if word == "input":
        state.update(Lookahead(lookahead_unop))
        return PartialCommand(src.ast.Input, [])
    raise Exception("Parsing error: expected a command, got " + word)
    
def parse_line(line : List[str], 
  result : Optional[PartialCommand], 
  state : ParserState) -> Optional[PartialCommand]:
    print(result)
    if len(line) == 0:
        return result
    if line[0].startswith("//"):
        return result
    word = line[0]
    nxt = line[1:]
    if result is None:
        comm = expect_command(word, PartialCommand(src.ast.Skip, []), state)
        return parse_line(nxt, comm, state)
    if isinstance(state.next, Lookahead):
        state.next.unpack(word, result, state)
        return parse_line(line, result, state)
    comm = state.next(word, result, state)
    if isinstance(result.cmd, src.ast.Seq):
        result.append(comm)
    print(result)
    return parse_line(nxt, result, state)

def parse(line : str, 
  result : Optional[PartialCommand], 
  state : ParserState) -> Optional[PartialCommand]:
    line = line.strip() # who needs whitespace anyway
    line = line.replace(";", " ;")
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
        raise Exception("Parsing error: incomplete final command " + str(result.cmd.__name__))
    return src.ast.Program(result)