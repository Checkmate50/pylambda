
"""
This is an auto-generated file, DO NOT TOUCH
Definitions are made by lc_defs.py and generated with lc_constants_macro.py
To update, see lc_defs/README.md
"""

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

def false_def(context : EmitContext) -> str:
    return f"(lambda x : lambda y : y)"
def false(context : EmitContext) -> str:
    return f"{app_lc(false_def, [], context)}"

functions_to_write.append(false_def)

def true_def(context : EmitContext) -> str:
    return f"(lambda x : lambda y : x)"
def true(context : EmitContext) -> str:
    return f"{app_lc(true_def, [], context)}"

functions_to_write.append(true_def)

def app_def(context : EmitContext) -> str:
    return f"(lambda x : lambda y : (x (y)))"
def app(x : str, y : str, context : EmitContext) -> str:
    return f"{app_lc(app_def, [x, y], context)}"

functions_to_write.append(app_def)

def pair_def(context : EmitContext) -> str:
    return f"(lambda x : lambda y : lambda f : (f (x) (y)))"
def pair(x : str, y : str, context : EmitContext) -> str:
    return f"{app_lc(pair_def, [x, y], context)}"

functions_to_write.append(pair_def)

def first_def(context : EmitContext) -> str:
    return f"(lambda x : (x ({false(context)})))"
def first(x : str, context : EmitContext) -> str:
    return f"{app_lc(first_def, [x], context)}"

functions_to_write.append(first_def)

def second_def(context : EmitContext) -> str:
    return f"(lambda x : (x ({false(context)})))"
def second(x : str, context : EmitContext) -> str:
    return f"{app_lc(second_def, [x], context)}"

functions_to_write.append(second_def)

def czero_def(context : EmitContext) -> str:
    return f"(lambda f : lambda x : x)"
def czero(context : EmitContext) -> str:
    return f"{app_lc(czero_def, [], context)}"

functions_to_write.append(czero_def)

def zero_def(context : EmitContext) -> str:
    return f"({pair(czero(context), czero(context), context)})"
def zero(context : EmitContext) -> str:
    return f"{app_lc(zero_def, [], context)}"

functions_to_write.append(zero_def)

def csucc_def(context : EmitContext) -> str:
    return f"(lambda n : (lambda f : lambda x : (f (n (f) (x)))))"
def csucc(n : str, context : EmitContext) -> str:
    return f"{app_lc(csucc_def, [n], context)}"

functions_to_write.append(csucc_def)

def cplus_def(context : EmitContext) -> str:
    return f"(lambda m : lambda n : (m ({mr(csucc, context)}) (n)))"
def cplus(m : str, n : str, context : EmitContext) -> str:
    return f"{app_lc(cplus_def, [m, n], context)}"

functions_to_write.append(cplus_def)

def cmult_def(context : EmitContext) -> str:
    return f"(lambda m : lambda n : (lambda f : (m (n (f)))))"
def cmult(m : str, n : str, context : EmitContext) -> str:
    return f"{app_lc(cmult_def, [m, n], context)}"

functions_to_write.append(cmult_def)

def cexp_def_def(context : EmitContext) -> str:
    return f"(lambda b : lambda e : (e (b)))"
def cexp_def(b : str, e : str, context : EmitContext) -> str:
    return f"{app_lc(cexp_def_def, [b, e], context)}"

functions_to_write.append(cexp_def_def)

def appfirst_def(context : EmitContext) -> str:
    return f"(lambda f : lambda p : ({pair(app('f', first('p', context), context), second('p', context), context)}))"
def appfirst(f : str, p : str, context : EmitContext) -> str:
    return f"{app_lc(appfirst_def, [f, p], context)}"

functions_to_write.append(appfirst_def)

def appsecond_def(context : EmitContext) -> str:
    return f"(lambda f : lambda p : ({pair(first('p', context), app('f', second('p', context), context), context)}))"
def appsecond(f : str, p : str, context : EmitContext) -> str:
    return f"{app_lc(appsecond_def, [f, p], context)}"

functions_to_write.append(appsecond_def)

def appboth_def(context : EmitContext) -> str:
    return f"(lambda f : lambda p : ({pair(app('f', first('p', context), context), app('f', second('p', context), context), context)}))"
def appboth(f : str, p : str, context : EmitContext) -> str:
    return f"{app_lc(appboth_def, [f, p], context)}"

functions_to_write.append(appboth_def)

def succ_def(context : EmitContext) -> str:
    return f"(lambda n : ({appfirst(mr(csucc, context), 'n', context)}))"
def succ(n : str, context : EmitContext) -> str:
    return f"{app_lc(succ_def, [n], context)}"

functions_to_write.append(succ_def)

def pred_def(context : EmitContext) -> str:
    return f"(lambda n : ({appsecond(mr(csucc, context), 'n', context)}))"
def pred(n : str, context : EmitContext) -> str:
    return f"{app_lc(pred_def, [n], context)}"

functions_to_write.append(pred_def)

def one_def(context : EmitContext) -> str:
    return f"({succ(zero(context), context)})"
def one(context : EmitContext) -> str:
    return f"{app_lc(one_def, [], context)}"

functions_to_write.append(one_def)

