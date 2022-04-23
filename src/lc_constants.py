
"""
This is an auto-generated file, DO NOT TOUCH
Definitions are made by lc_defs.py and generated with lc_constants_macro.py
To update, see lc_defs/README.md
"""

from src.util import *
import inspect
from typing import Set, List

lc_inspector = """
import inspect

class LambdaInspect:
    def __init__(self, name : str = ""):
        self.name = name
        self.abstractions = []
        self.callees = []
        self.executing = False

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.name

    def output(self, calls):
        if self in calls:
            return self.name
        calls.add(self)
        a = ""
        for layer in self.abstractions:
            for item in layer:
                a += f"lambda {item} : "
        if len(a) > 0:
            a += "("
        clsp = ')' if len(a) > 0 else ''
        if not self.name:
            return f"{a}{' '.join(f'{x.output(calls)}' for x in self.callees)}{clsp}"
        
        spc = ' ' if len(self.callees) > 0 else ''
        cs = ' '.join(['({})'.format(x.output(calls)) for x in self.callees])
        return f"{a}{self.name}{spc}{cs}{clsp}"

    def resolve(self, vars, calls):
        if self in calls:
            return self
        calls.add(self)
        for index in range(len(self.callees)):
            while inspect.isfunction(self.callees[index]):
                var = str(self.callees[index].__code__.co_varnames[0]) + "0"
                while var in vars:
                    last_number = -1
                    for i in range(len(var)-1,-1,-1):
                        if not var[i].isdigit():
                            last_number = i
                            break
                    var = var[:last_number+1] + str(int(var[last_number+1:]) + 1)
                vars.add(var)
                self.abstractions[index].append(var)
                self.callees[index] = self.callees[index](LambdaInspect(var))
        for callee in self.callees:
            if isinstance(callee, LambdaInspect):
                callee.resolve(vars, calls)
        return self

    def __call__(self, other):
        self.abstractions.append([])
        self.callees.append(other)
        return self
"""

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
    
    def no_input(self):
        return self.cli.contains("no-input")

    def __repr__(self):
        return "EMIT_CONTEXT" + str(self.cli)

functions_to_write = []

def retrieve_name_constant(var : any) -> List[str]:
    callers_local_vars = inspect.currentframe().f_globals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]

# maybe_replace is too long to type
def mr(val, context : EmitContext) -> str:
    if context.debug():
        return f"{retrieve_name_constant(val)[0].upper().split('_')[0]}"
    def_name = val.__name__
    if not def_name.endswith("_def"):        
        def_name = f"{def_name}_def"
    return f"{globals()[def_name](context)}"

def app_lc(f, args : List[str], context : EmitContext) -> str:
    return f"{mr(f, context)}{' ' if len(args) > 0 else ''}{' '.join(['({})'.format(x) for x in args])}"

def emit_runtime_error_thunk(message : str, context : EmitContext) -> str:
    return f"lambda:_raise(RuntimeError(\"{message}\"))"

def app_def(context : EmitContext) -> str:
    return f"(lambda _x : lambda _y : (_x (_y)))"
def app(x : str, y : str, context : EmitContext) -> str:
    return f"{app_lc(app_def, [x, y], context)}"

functions_to_write.append(app_def)

def app2_def(context : EmitContext) -> str:
    return f"(lambda _x : lambda _y : lambda _z : (_x (_y) (_z)))"
def app2(x : str, y : str, z : str, context : EmitContext) -> str:
    return f"{app_lc(app2_def, [x, y, z], context)}"

functions_to_write.append(app2_def)

def thunk_def(context : EmitContext) -> str:
    return f"(lambda _x : (lambda:_x))"
def thunk(x : str, context : EmitContext) -> str:
    return f"{app_lc(thunk_def, [x], context)}"

functions_to_write.append(thunk_def)

def false_def(context : EmitContext) -> str:
    return f"(lambda _x : lambda _y : _y)"
def false(context : EmitContext) -> str:
    return f"{app_lc(false_def, [], context)}"

functions_to_write.append(false_def)

def true_def(context : EmitContext) -> str:
    return f"(lambda _x : lambda _y : _x)"
def true(context : EmitContext) -> str:
    return f"{app_lc(true_def, [], context)}"

functions_to_write.append(true_def)

def lif_def(context : EmitContext) -> str:
    return f"(lambda _b : lambda _c : lambda _d : (_b (_c) (_d)))"
def lif(b : str, c : str, d : str, context : EmitContext) -> str:
    return f"{app_lc(lif_def, [b, c, d], context)}"

functions_to_write.append(lif_def)

def lnot_def(context : EmitContext) -> str:
    return f"(lambda _b : ({lif('_b', false(context), true(context), context)}))"
def lnot(b : str, context : EmitContext) -> str:
    return f"{app_lc(lnot_def, [b], context)}"

functions_to_write.append(lnot_def)

def land_def(context : EmitContext) -> str:
    return f"(lambda _b1 : lambda _b2 : ({lif('_b1', '_b2', false(context), context)}))"
def land(b1 : str, b2 : str, context : EmitContext) -> str:
    return f"{app_lc(land_def, [b1, b2], context)}"

functions_to_write.append(land_def)

def lor_def(context : EmitContext) -> str:
    return f"(lambda _b1 : lambda _b2 : ({lif('_b1', true(context), '_b2', context)}))"
def lor(b1 : str, b2 : str, context : EmitContext) -> str:
    return f"{app_lc(lor_def, [b1, b2], context)}"

functions_to_write.append(lor_def)

def xor_def(context : EmitContext) -> str:
    return f"(lambda _b1 : lambda _b2 : ({lif('_b1', lnot('_b2', context), '_b2', context)}))"
def xor(b1 : str, b2 : str, context : EmitContext) -> str:
    return f"{app_lc(xor_def, [b1, b2], context)}"

functions_to_write.append(xor_def)

def pair_def(context : EmitContext) -> str:
    return f"(lambda _x : lambda _y : (lambda _f : (_f (_x) (_y))))"
def pair(x : str, y : str, context : EmitContext) -> str:
    return f"{app_lc(pair_def, [x, y], context)}"

functions_to_write.append(pair_def)

def first_def(context : EmitContext) -> str:
    return f"(lambda _x : (_x ({true(context)})))"
def first(x : str, context : EmitContext) -> str:
    return f"{app_lc(first_def, [x], context)}"

functions_to_write.append(first_def)

def second_def(context : EmitContext) -> str:
    return f"(lambda _x : (_x ({false(context)})))"
def second(x : str, context : EmitContext) -> str:
    return f"{app_lc(second_def, [x], context)}"

functions_to_write.append(second_def)

def czero_def(context : EmitContext) -> str:
    return f"(lambda _f : lambda _x : _x)"
def czero(context : EmitContext) -> str:
    return f"{app_lc(czero_def, [], context)}"

functions_to_write.append(czero_def)

def csucc_def(context : EmitContext) -> str:
    return f"(lambda _n : (lambda _f : lambda _x : (_f (_n (_f) (_x)))))"
def csucc(n : str, context : EmitContext) -> str:
    return f"{app_lc(csucc_def, [n], context)}"

functions_to_write.append(csucc_def)

def cplus_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({app2('_n', mr(csucc, context), '_m', context)}))"
def cplus(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(cplus_def, [n, m], context)}"

functions_to_write.append(cplus_def)

def cmult_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : (lambda _f : (_n (_m (_f)))))"
def cmult(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(cmult_def, [n, m], context)}"

functions_to_write.append(cmult_def)

def cexp_def(context : EmitContext) -> str:
    return f"(lambda _b : lambda _e : (_e (_b)))"
def cexp(b : str, e : str, context : EmitContext) -> str:
    return f"{app_lc(cexp_def, [b, e], context)}"

functions_to_write.append(cexp_def)

def ctwo_def(context : EmitContext) -> str:
    return f"({csucc(csucc(czero(context), context), context)})"
def ctwo(context : EmitContext) -> str:
    return f"{app_lc(ctwo_def, [], context)}"

functions_to_write.append(ctwo_def)

def appfirst_def(context : EmitContext) -> str:
    return f"(lambda _f : lambda _p : ({pair(app('_f', first('_p', context), context), second('_p', context), context)}))"
def appfirst(f : str, p : str, context : EmitContext) -> str:
    return f"{app_lc(appfirst_def, [f, p], context)}"

functions_to_write.append(appfirst_def)

def appsecond_def(context : EmitContext) -> str:
    return f"(lambda _f : lambda _p : ({pair(first('_p', context), app('_f', second('_p', context), context), context)}))"
def appsecond(f : str, p : str, context : EmitContext) -> str:
    return f"{app_lc(appsecond_def, [f, p], context)}"

functions_to_write.append(appsecond_def)

def zero_def(context : EmitContext) -> str:
    return f"({pair(czero(context), czero(context), context)})"
def zero(context : EmitContext) -> str:
    return f"{app_lc(zero_def, [], context)}"

functions_to_write.append(zero_def)

def succ_def(context : EmitContext) -> str:
    return f"(lambda _n : ({appfirst(mr(csucc, context), '_n', context)}))"
def succ(n : str, context : EmitContext) -> str:
    return f"{app_lc(succ_def, [n], context)}"

functions_to_write.append(succ_def)

def pred_def(context : EmitContext) -> str:
    return f"(lambda _n : ({appsecond(mr(csucc, context), '_n', context)}))"
def pred(n : str, context : EmitContext) -> str:
    return f"{app_lc(pred_def, [n], context)}"

functions_to_write.append(pred_def)

def one_def(context : EmitContext) -> str:
    return f"({succ(zero(context), context)})"
def one(context : EmitContext) -> str:
    return f"{app_lc(one_def, [], context)}"

functions_to_write.append(one_def)

def two_def(context : EmitContext) -> str:
    return f"({succ(one(context), context)})"
def two(context : EmitContext) -> str:
    return f"{app_lc(two_def, [], context)}"

functions_to_write.append(two_def)

def neg_def(context : EmitContext) -> str:
    return f"(lambda _n : ({pair(second('_n', context), first('_n', context), context)}))"
def neg(n : str, context : EmitContext) -> str:
    return f"{app_lc(neg_def, [n], context)}"

functions_to_write.append(neg_def)

def plus_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({pair(app2(mr(cplus, context), first('_n', context), first('_m', context), context), app2(mr(cplus, context), second('_n', context), second('_m', context), context), context)}))"
def plus(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(plus_def, [n, m], context)}"

functions_to_write.append(plus_def)

def minus_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({pair(app2(mr(cplus, context), first('_n', context), second('_m', context), context), app2(mr(cplus, context), second('_n', context), first('_m', context), context), context)}))"
def minus(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(minus_def, [n, m], context)}"

functions_to_write.append(minus_def)

def mult_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({pair(app2(mr(cplus, context), app2(mr(cmult, context), first('_n', context), first('_m', context), context), app2(mr(cmult, context), second('_n', context), second('_m', context), context), context), app2(mr(cplus, context), app2(mr(cmult, context), first('_n', context), second('_m', context), context), app2(mr(cmult, context), second('_n', context), first('_m', context), context), context), context)}))"
def mult(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(mult_def, [n, m], context)}"

functions_to_write.append(mult_def)

def ciszero_def(context : EmitContext) -> str:
    return f"(lambda _n : (_n (lambda _x : {false(context)}) ({true(context)})))"
def ciszero(n : str, context : EmitContext) -> str:
    return f"{app_lc(ciszero_def, [n], context)}"

functions_to_write.append(ciszero_def)

def cphi_def(context : EmitContext) -> str:
    return f"(lambda _x : ({pair(second('_x', context), csucc(second('_x', context), context), context)}))"
def cphi(x : str, context : EmitContext) -> str:
    return f"{app_lc(cphi_def, [x], context)}"

functions_to_write.append(cphi_def)

def cpred_def(context : EmitContext) -> str:
    return f"(lambda _n : ({first(app2('_n', mr(cphi, context), pair(czero(context), czero(context), context), context), context)}))"
def cpred(n : str, context : EmitContext) -> str:
    return f"{app_lc(cpred_def, [n], context)}"

functions_to_write.append(cpred_def)

def csub_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({app2('_m', mr(cpred, context), '_n', context)}))"
def csub(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(csub_def, [n, m], context)}"

functions_to_write.append(csub_def)

def cleq_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({ciszero(csub('_n', '_m', context), context)}))"
def cleq(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(cleq_def, [n, m], context)}"

functions_to_write.append(cleq_def)

def ceq_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({land(cleq('_n', '_m', context), cleq('_m', '_n', context), context)}))"
def ceq(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(ceq_def, [n, m], context)}"

functions_to_write.append(ceq_def)

def clt_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({land(cleq('_n', '_m', context), lnot(cleq('_m', '_n', context), context), context)}))"
def clt(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(clt_def, [n, m], context)}"

functions_to_write.append(clt_def)

def eq_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({ceq(cplus(first('_n', context), second('_m', context), context), cplus(second('_n', context), first('_m', context), context), context)}))"
def eq(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(eq_def, [n, m], context)}"

functions_to_write.append(eq_def)

def leq_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({cleq(cplus(first('_n', context), second('_m', context), context), cplus(second('_n', context), first('_m', context), context), context)}))"
def leq(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(leq_def, [n, m], context)}"

functions_to_write.append(leq_def)

def geq_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({leq('_m', '_n', context)}))"
def geq(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(geq_def, [n, m], context)}"

functions_to_write.append(geq_def)

def lt_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({land(leq('_n', '_m', context), lnot(eq('_n', '_m', context), context), context)}))"
def lt(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(lt_def, [n, m], context)}"

functions_to_write.append(lt_def)

def gt_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({lt('_m', '_n', context)}))"
def gt(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(gt_def, [n, m], context)}"

functions_to_write.append(gt_def)

def collapse_def(context : EmitContext) -> str:
    return f"(lambda _n : ({lif(clt(second('_n', context), first('_n', context), context), csub(first('_n', context), second('_n', context), context), csub(second('_n', context), first('_n', context), context), context)}))"
def collapse(n : str, context : EmitContext) -> str:
    return f"{app_lc(collapse_def, [n], context)}"

functions_to_write.append(collapse_def)

def z_def(context : EmitContext) -> str:
    return f"(lambda _rec : ((lambda _x : _rec (lambda _v : _x (_x) (_v))) (lambda _x : _rec (lambda _v : _x (_x) (_v)))))"
def z(rec : str, context : EmitContext) -> str:
    return f"{app_lc(z_def, [rec], context)}"

functions_to_write.append(z_def)

def cdiv_def(context : EmitContext) -> str:
    return f"({mr(z_def, context)}(lambda _rec : lambda _n : lambda _m : (({lif(ciszero('_m', context), emit_runtime_error_thunk('Divide by zero', context), thunk('('+lif(clt('_n', '_m', context), thunk(czero(context), context), '(lambda:'+csucc(app2('_rec', csub('_n', '_m', context), '_m', context), context)+')', context), context)+')()', context)})())))"
def cdiv(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(cdiv_def, [n, m], context)}"

functions_to_write.append(cdiv_def)

def cmod_def(context : EmitContext) -> str:
    return f"({mr(z_def, context)}(lambda _rec : lambda _n : lambda _m : (({lif(ciszero('_m', context), emit_runtime_error_thunk('Mod by zero', context), thunk('('+lif(clt('_n', '_m', context), thunk('_n', context), '(lambda:'+app2('_rec', csub('_n', '_m', context), '_m', context)+')', context), context)+')()', context)})())))"
def cmod(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(cmod_def, [n, m], context)}"

functions_to_write.append(cmod_def)

def div_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : ({lif(xor(clt(second('_n', context), first('_n', context), context), clt(second('_m', context), first('_m', context), context), context), pair(czero(context), cdiv(collapse('_n', context), collapse('_m', context), context), context), pair(cdiv(collapse('_n', context), collapse('_m', context), context), czero(context), context), context)}))"
def div(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(div_def, [n, m], context)}"

functions_to_write.append(div_def)

def mod_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : (({lif(lor(clt(first('_n', context), second('_n', context), context), clt(first('_m', context), second('_m', context), context), context), emit_runtime_error_thunk('Mod not permitted with negatives', context), thunk(pair(cmod(collapse('_n', context), collapse('_m', context), context), czero(context), context), context), context)})()))"
def mod(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(mod_def, [n, m], context)}"

functions_to_write.append(mod_def)

def exponent_def(context : EmitContext) -> str:
    return f"(lambda _n : lambda _m : (({lif(clt(first('_m', context), second('_m', context), context), emit_runtime_error_thunk('Negative exponent not permitted', context), thunk(lif(lor(cleq(second('_n', context), first('_n', context), context), ciszero(cmod(collapse('_m', context), ctwo(context), context), context), context), pair(cexp(collapse('_n', context), collapse('_m', context), context), czero(context), context), pair(czero(context), cexp(collapse('_n', context), collapse('_m', context), context), context), context), context), context)})()))"
def exponent(n : str, m : str, context : EmitContext) -> str:
    return f"{app_lc(exponent_def, [n, m], context)}"

functions_to_write.append(exponent_def)

