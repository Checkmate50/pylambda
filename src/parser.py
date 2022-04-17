import src.ast as ast
from src.util import *
from typing import List, Optional, Union

reserved = ("true", "false", "print", "input", "output", "while", "if", "else")

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
    def __init__(self, message : str, state):
        super().__init__("Parsing error on line " + str(state.line_number) + ": " + str(message))

class ParsingExpectException(ParsingException):
    def __init__(self, expect : str, word : str, state):
        super().__init__("expected " + str(expect) + ", got " + str(word), state)

class ParsingState(BaseClass):
    pass

class DefaultState(ParsingState):
    def __init__(self):
        pass
    def __repr__(self):
        return "DEFAULT STATE"

class ConditionState(ParsingState):
    def __init__(self):
        pass
    def __repr__(self):
        return "DEFAULT STATE"

class Lookahead(BaseClass):
    def __init__(self, lookahead):
        if not (lookahead == lookahead_binop or lookahead == lookahead_expr):
            raise InternalException("expected lookahead, got " + str(lookahead))
        self.lookahead = lookahead
    def __repr__(self):
        return "LOOKAHEAD " + str(self.unpack.__name__)

class PartialASTElement(BaseClass):
    def __init__(self, cmd : ast.Statement, args : List[BaseClass]):
        self.cmd = cmd
        self.args = args
        self.index_update = -1
        self.index = -1

    def index_check(self, fun : str):
        if not isinstance(self.args[self.index], PartialASTElement):
                raise InternalException("Attempting to " + str(fun) + " on non-Partial element " + 
                str(self.args[self.index]) + " at index " + str(self.index))

    def set_index(self, arg : BaseClass):
        # Ok, this is _super_ janky, but control flow for Statement appending is mostly done here
        if self.cmd == ast.Seq:
            self.index = 2
        elif isinstance(arg, PartialExpression):
            self.index = len(self.args)-1
        elif self.index_update > -1:
            self.index += self.index_update

    def clear_index(self):
        if self.index == -1:
            if self.cmd == ast.Else:
                return # special casing the no-argument Else statement
            raise InternalException("Attempting to clear non-indexed Element " + str(self))
        self.index_check("clear_index")
        if isinstance(self.args[self.index], PartialExpression):
            self.index = -1
        else:
            self.args[self.index].clear_index()

    def update_index(self, amount : int):
        self.index_update = amount

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

    def pack(self, state):
        try:
            packed = [arg.pack(state) if isinstance(arg, PartialASTElement) else arg for arg in self.args]
            return self.cmd(*packed)
        except TypeError:
            raise ParsingException("wrong number of arguments to " +
                str(self.cmd.__name__) + " (" + str(len(self.args)) + " given)", state)

    def is_partial(self):
        return isinstance(self.cmd, PartialASTElement)

class PartialStatement(PartialASTElement):
    def __repr__(self):
        return "PARTIAL_STATEMENT " + str(self.cmd) + " " + str(self.args) + " " + str(self.index)

class PartialExpression(PartialASTElement):
    def __repr__(self):
        return "PARTIAL_EXPRESSION " + str(self.cmd) + " " + str(self.args) + " " + str(self.index)

class ParserState(BaseClass):
    def __init__(self):
        self.next = None
        self.clear_state()
        self.line_number = 0
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

    def clear_state(self):
        self.state = DefaultState()

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
            raise ParsingException("Unmatched )", self)
        while (is_paren and not self.ops[-1].cmd == OpenParen) or (not is_paren and self.ops):
            if not is_paren and self.ops[-1].cmd == OpenParen:
                raise ParsingException("Unmatched (", self)
            self.pop_op()
            if is_paren and not self.ops:
                raise ParsingException("Unmatched )", self)
        if is_paren and self.ops[-1].cmd == OpenParen:
            self.pop_op()
        if not is_paren:
            while self.args:
                result.append(self.pop_arg())

    def scope_in(self, cmd : PartialASTElement):
        typecheck(cmd, PartialASTElement)
        cmd.clear_index()
        cmd.update_index(3)
        self.scope.append(cmd)
    def scope_out(self) -> PartialASTElement:
        result = self.scope.pop()
        return result

    def __repr__(self):
        return "STATE: " + str(self.next)

# So it's sorta weird, but these lookahead functions "manage" the control flow of the parser
def lookahead_binop(word : str, result : PartialStatement, state : ParserState):
    if not isinstance(state.state, ConditionState) and word == ";":
        state.update(expect_semi)
    elif isinstance(state.state, ConditionState) and word == "{":
        state.update(expect_open_block)
    elif word == ")":
        state.update(expect_close_paren)
    else:
        state.update(expect_binop)

def lookahead_expr(word : str, result : PartialStatement, state : ParserState):
    if word in ("-", "not"):
        state.update(expect_unop)
    elif word == "(":
        state.update(expect_open_paren)
    else:
        state.update(expect_const)

def expect_semi(word : str, result : PartialStatement, state : ParserState) -> PartialASTElement:
    if not word == ";":
        raise InternalException("Expected ; got " + str(word))
    state.update(expect_statement)
    state.clean_ops(result, False)
    return PartialStatement(ast.Seq, [state.line_number, result.pack(state)])

def expect_open_block(word :str, result : PartialStatement, state : ParserState) -> PartialExpression:
    if not word == "{":
        raise ParsingExpectException("Expected { got ", word, state)
    state.update(expect_statement)
    state.clean_ops(result, False)
    state.clear_state()
    state.scope_in(result)
    return None

def expect_close_paren(word :str, result : PartialStatement, state : ParserState) -> PartialExpression:
    if not word == ")":
        raise InternalException("Expected ) got " + str(word))
    state.update(Lookahead(lookahead_binop))
    state.clean_ops(result, True)
    return result

def expect_binop(word : str, result : PartialStatement, state : ParserState) -> PartialExpression:
    if word in ("+", "-", "*", "^", "==", "<", ">", "<=", ">=", "and", "or"):
        state.update(Lookahead(lookahead_expr))
        state.push_op(PartialExpression(ast.Binop, [ast.Op(word)]))
        return result
    raise ParsingExpectException("binary operation", word, state)

def expect_unop(word : str, result : PartialStatement, state : ParserState) -> PartialExpression:
    if not (word == "-" or word == "not"):
        raise InternalException("Expected Unop got " + str(word))
    state.update(Lookahead(lookahead_expr))
    state.push_op(PartialExpression(ast.Unop, [(ast.Op(word))])) # we can do this cause we already did the lookahead
    return result

def expect_open_paren(word :str, result : PartialStatement, state : ParserState) -> PartialExpression:
    if not word == "(":
        raise InternalException("Expected ( got " + str(word))
    state.update(Lookahead(lookahead_expr))
    state.push_op(PartialExpression(OpenParen, []))
    return result

def expect_const(word : str, result : PartialStatement, state : ParserState) -> PartialASTElement:
    state.update(Lookahead(lookahead_binop))
    if word.isdigit():
        state.push_arg(PartialExpression(ast.Const, [ast.Number(int(word))]))
    elif word == "true":
        state.push_arg(PartialExpression(ast.Const, [ast.Bool(True)]))
    elif word == "false":
        state.push_arg(PartialExpression(ast.Const, [ast.Bool(False)]))
    elif word in reserved:
        raise ParsingException("use of reserved keyword as variable " + word, state)
    elif word.isidentifier():
        state.push_arg(PartialExpression(ast.Var, [word]))
    else:
        raise ParsingExpectException("constant, unary operation, or variable", word, state)
    return result

def expect_assign(word : str, result : PartialStatement, state : ParserState) -> PartialASTElement:
    if word != "=":
        raise ParsingExpectException("=", word, state)
    state.update(Lookahead(lookahead_expr))
    return result # No append, just looking stuff up

def expect_var(word : str, result : PartialStatement, state : ParserState) -> PartialASTElement:
    if word in reserved:
        raise ParsingException("use of reserved keyword as variable " + word, state)
    if not word.isidentifier():
        raise ParsingExpectException("variable", word, state)
    state.update(expect_semi)
    result.append(ast.Var(word))
    return result

def expect_statement(word : str, result : Optional[PartialStatement], state : ParserState) -> PartialStatement:
    if word == "skip":
        state.update(expect_semi)
        cmd = PartialStatement(ast.Skip, [state.line_number])
    elif word == "print":
        state.update(Lookahead(lookahead_expr))
        cmd = PartialStatement(ast.Print, [state.line_number])
    elif word == "input":
        state.update(expect_var)
        cmd = PartialStatement(ast.Input, [state.line_number])
    elif word == "if":
        state.update(Lookahead(lookahead_expr))
        state.set_state(ConditionState())
        cmd = PartialStatement(ast.If, [state.line_number])
    elif word == "elif":
        state.update(Lookahead(lookahead_expr))
        state.set_state(ConditionState())
        cmd = PartialStatement(ast.Elif, [state.line_number])
    elif word == "else":
        state.update(expect_open_block)
        cmd = PartialStatement(ast.Else, [state.line_number])
    elif word == "while":
        state.update(Lookahead(lookahead_expr))
        state.set_state(ConditionState())
        cmd = PartialStatement(ast.While, [state.line_number])
    elif word == "}":
        outer = state.scope_out()
        outer.append(result)
        cmd = PartialStatement(ast.Seq, [state.line_number, outer.pack(state)])
        return cmd
    elif word in reserved:
        raise ParsingException("attempting to assign to reserved keyword " + str(word), state)
    elif word.isidentifier():
        state.update(expect_assign)
        cmd = PartialStatement(ast.Assign, [state.line_number, ast.Var(word)])
    else:
        raise ParsingExpectException("a Statement", word, state)
    if result is None:
        return cmd
    result.append(cmd)
    return result
    
def parse_line(line : List[str], 
  result : Optional[PartialStatement], 
  state : ParserState) -> Optional[PartialStatement]:
    while line:
        if line[0].startswith("//"): #Comments 
            return result
        word = line[0]
        if result is None:
            result = expect_statement(word, None, state)
            line.pop(0)
        elif isinstance(state.next, Lookahead):
            state.next.lookahead(word, result, state)
        else:
            result = state.next(word, result, state)
            line.pop(0)
    return result

def parse(line : str, 
  result : Optional[PartialStatement], 
  state : ParserState) -> Optional[PartialStatement]:
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
            state.line_number += 1
    if len(state.scope) > 0:
        raise ParsingException("unclosed scope (did you forget a '}'?)", state)
    if result is None:
        return ast.Program(ast.Skip)  # default program
    try:
        result = result.pack(state)
    except:
        raise ParsingException("incomplete final Statement " + str(result.cmd.__name__), state)
    return ast.Program(result)