from typing import List, Text, TextIO
from io import TextIOWrapper
import re

PRED_STRING = """
\"\"\"
This is an auto-generated file, DO NOT TOUCH
Definitions are made by lc_defs.py and generated with lc_constants_macro.py
To update, see lc_defs/README.md
\"\"\"

from src.util import *
import inspect
from typing import Set, List

class CLI:
    def __init__(self, args : Set[str] = set()):
        self.set_args(args)

    def set_args(self, args : List[str]):
        for i in range(len(args)):
            if not args[i].startswith("--") or len(args[i]) < 2:
                raise Exception("Invalid argument " + str(args[i]))
            args[i] = args[i][2:]
        self.args = set(args)

    def contains(self, arg : str) -> bool:
        return arg in self.args

    def __repr__(self):
        return "CLI: " + str(self.args)

class EmitContext(BaseClass):
    def __init__(self, cli : CLI):
        self.cli = cli
        self.interp : bool = False

    def raw(self):
        return self.cli.contains("raw")

    def debug(self):
        return self.cli.contains("debug")

    def __repr__(self):
        return "EMIT_CONTEXT" + str(self.cli)

functions_to_write = []

def retrieve_name_constant(var : any) -> List[str]:
    callers_local_vars = inspect.currentframe().f_globals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]

# maybe_debug is too long to type
def mr(val, context : EmitContext) -> str:
    if context.debug():
        return f"{retrieve_name_constant(val)[0].upper().split('_')[0]}"
    def_name = val.__name__
    if not def_name.endswith("_def"):        
        def_name = f"{def_name}_def"
    return f"{globals()[def_name](context)}"

def app_lc(f, args : List[str], context : EmitContext) -> str:
    return f"{mr(f, context)}{' ' if len(args) > 0 else ''}{' '.join(['({})'.format(x) for x in args])}"
"""

def parse_defs(f : TextIOWrapper, data) -> List[List[str]]:
    expect_return = False
    for line in f:
        line = line.strip()
        if expect_return:
            if not line.startswith("return"):
                raise Exception("Invalid line, expected return, got " + line)
            data[-1].append(line)
            expect_return = False
            continue
        if line.startswith("def"):
            data.append([line])
            expect_return = True

def write_def(line0 : str, f : TextIOWrapper):
    name = line0.split("(")[0]
    f.write(f"{name}_def(context : EmitContext) -> str:")
    f.write("\n")

def write_def_body(line0 : str, line1 : str, f : TextIOWrapper):
    args = line0.split("(")[1].split(")")[0].split(",")
    args = [arg.strip() for arg in args]
    if args[0] == '':
        args = []
    f.write(f"    return f\"(")
    for arg in args:
        f.write(f"lambda {arg} : ")
    if len(args) > 0:
        f.write("(")
    line1 = line1.split('"')[1]
    for arg in args:
        line1 = line1.replace(f"{{{arg}}}", f"{arg}")
        line1 = re.sub(rf"([a-z]\(([a-z]*(\(\))?,\s)*){arg}((,\s[a-z\(]*)*\))", fr"\1'{arg}'\4", line1)
    # manual regex-like crap cause matching is hard
    marks = []
    in_raw = False
    str_start = -1
    in_quotes = False
    for i in range(len(line1)):
        if line1[i] == "{":
            in_raw = True
        if line1[i] == "}":
            in_raw = False
        if in_raw and line1[i] == "'":
            in_quotes = not in_quotes
        if in_raw and str_start == -1 and line1[i].isalpha() and not in_quotes: # ignoring variables cleverly
            str_start = i
            continue
        if str_start != -1 and not line1[i].isalpha():
            if line1[i] != "(":
                marks.append((str_start, i))
            str_start = -1
    for i in marks[::-1]: # go in reverse to avoid string update shenanigans
        line1 = f"{line1[:i[0]]}mr({line1[i[0]:i[1]]}){line1[i[1]:]}"
    valid_count = 0
    marks = []
    for item in range(len(line1)):        
        if line1[item] == "(" and line1[item-1].isalpha():
            valid_count += 1
        if line1[item] == ")" and valid_count > 0:
            valid_count -= 1
            marks.append(item)
    for i in marks[::-1]: # go in reverse to avoid string update shenanigans
        c = "context"
        if line1[i-1] != "(":
            c = ", " + c
        line1 = f"{line1[:i]}{c}{line1[i:]}"
    f.write(line1)
    f.write((")" if len(args) > 0 else "") + ")\"")
    f.write("\n")

def write_fn(line0 : str, f : TextIOWrapper):
    result = line0.split("(")
    result[1] = result[1].split(")")[0]
    result[1] = result[1].split(",")
    if result[1] == ['']: #stupid special case
        result[1] = []
    for i in range(len(result[1])):
        result[1][i] = result[1][i].strip() + " : str"
    result[1].append("context : EmitContext")
    result = "(".join([result[0], ", ".join(result[1])])
    result = result + ") -> str:"
    f.write(result)
    f.write("\n")

def write_fn_body(line0 : str, f : TextIOWrapper):
    name = line0.split("(")[0].split(" ")[1]
    args = line0.split("(")[1].split(")")[0].split(",")
    args = f"[{', '.join([arg.strip() for arg in args])}]"
    f.write(f"    return f\"{{app_lc({name}_def, {args}, context)}}\"")
    f.write("\n\n")

def write_append(line0 : str, f : TextIOWrapper):
    name = line0.split("(")[0].split(" ")[1]
    f.write(f"functions_to_write.append({name}_def)")
    f.write("\n\n")

def main():
    data : List[List[str]] = []
    with open("src/lc_defs/lc_defs.py", 'r') as f:
        parse_defs(f, data)
    
    with open("src/lc_constants.py", 'w') as f:
        f.write(PRED_STRING)
        f.write("\n")
        for line in data:
            # We're assuming a lot about line structure
            write_def(line[0], f)
            write_def_body(line[0], line[1], f)
            write_fn(line[0], f)
            write_fn_body(line[0], f)
            write_append(line[0], f)

if __name__ == "__main__":
    main()
