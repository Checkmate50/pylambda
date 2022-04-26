"""
Given a syntactically-valid pylambda program
Produces a python code result
Note that we assume valid pylambda code, things _will break_ if it's not
Note also that any `input` will be replaced with 0
"""

from sys import argv
from typing import List

class ReadState:
    def __init__(self):
        self.index = 0
        self.scope = 0
    
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return f"READSTATE: {self.index} {self.scope}"

def help():
    print("Expected args: python pylambda_to_python.py name_of_file.pylambda")

# Literally the laziest lexing imaginable
# Just ignore literally all external whitespace, and parse the internal stuff
def lex_file(filename : str) -> List[str]:
    result = []
    with open(filename, 'r') as f:
        for line in f:
            # we only care about `;{}` being parsed properly
            line = line.replace(";", " ; ").replace("{", " { ").replace("}", " } ")
            result += line.strip().split("//")[0].split()
    return result

# Update state.index as we go, but parse a single command (until { or ;)
def parse_command(inp : List[str], state : ReadState) -> str:
    token = inp[state.index]
    state.index += 1
    result = []
    parsing_print = False
    parsing_input = False
    if token != "skip":
        result.append(token)
    if token == "print": # Special case for pylambda
        result.append("(")
        parsing_print = True
    if token == "input":
        parsing_input = True
    while token not in (';', '{', '}') and state.index < len(inp): # we actually don't care about the middle at all
        token = inp[state.index]
        state.index += 1
        if token == '^': # Special case for exponentiation
            result.append("**")
        elif token == '/': # Division stuff
            result.append("//")
        elif token in ("true", "false"):
            result.append(token.capitalize())
        else:
            result.append(token)
    if parsing_print:
        result.insert(-1, ')')
    if parsing_input:
        # We use a dummy input for this
        result = result[1:-1] + ["= 0"] + [result[-1]]
    if token == '{':
        result[-1] = ':'
        state.scope += 1
    elif token == '}':
        result.pop()
        if state.scope <= 0:
            raise Exception("Unmatched }")
        state.scope -= 1
    elif token == ';':
        result.pop()
    return ' '.join(result)

def to_python(inp : List[str]) -> str:
    state = ReadState()
    result = ""
    while state.index < len(inp):
        result += ("  " * state.scope) + parse_command(inp, state) + "\n"
    return result

def main():
    if len(argv) < 2:
        help()
        exit()
    print(to_python(lex_file(argv[1])))

if __name__=="__main__":
    main()