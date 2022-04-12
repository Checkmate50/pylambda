import src.ast
from src.util import *
from typing import List, Optional

class Lookahead(AbstractClass):
    def __init__(self, lookahead):
        if not (lookahead == lookahead_semi or lookahead == lookahead_unop):
            raise Exception("Internal Error, expected lookahead, got " + str(lookahead))
        self.lookahead = lookahead
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
        self.index = -1
    def append(self, arg : AbstractClass):
        if self.index == -1:
            self.args.append(arg)
            # Ok, this is _super_ janky, but control flow for command appending is done here
            if self.cmd == src.ast.Seq:
                self.index = 1
        else:
            print(self)
            self.args[self.index].append(arg) # Wow, that's a lotta recursion
    def unpack(self):
        unpacked = [arg.unpack() if isinstance(arg, PartialCommand) else arg for arg in self.args]
        return self.cmd(*unpacked)
    def is_partial(self):
        return isinstance(self.cmd, PartialCommand)
    def __str__(self):
        return "PARTIALCOMMAND " + str(self.cmd) + " " + str(self.args)

# So it's sorta weird, but these lookahead functions "manage" the control flow of the parser
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
def expect_unop(word : str, result : PartialCommand, state : ParserState) -> PartialCommand:
    state.update(Lookahead(lookahead_unop))
    result.append(src.ast.Op(word)) # we can do this cause we already did the lookahead
    return result

def expect_command(word : str, result : Optional[PartialCommand], state : ParserState) -> PartialCommand:
    if word == "skip":
        state.update(expect_semi)
        cmd = PartialCommand(src.ast.Skip, [])
        result.append()
    elif word == "print":
        state.update(Lookahead(lookahead_unop))
        cmd = PartialCommand(src.ast.Print, [])
    elif word == "input":
        state.update(Lookahead(lookahead_unop))
        cmd = PartialCommand(src.ast.Input, [])
    else:
        raise Exception("Parsing error: expected a command, got " + word)
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