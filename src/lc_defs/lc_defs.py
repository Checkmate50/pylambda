"""
So basically this is a meta-file to be used by lc_constants_macro
We make it a py file for linting, but this file alone will not do what we want
"""

# dummy class for typing -- we use a class to avoid being parsed
class emit_runtime_error_thunk():
    pass

def app(x, y):
    return f"{x} ({y})"
def app2(x, y, z):
    return f"{x} ({y}) ({z})"
def thunk(x):
    return f"lambda:{x}"

def false():
    return "lambda _x : lambda _y : _y"
def true():
    return "lambda _x : lambda _y : _x"
def lif(b, c, d):
    return f"{b} ({c}) ({d})"

def lnot(b):
    return f"{lif(b, false(), true())}"
def land(b1, b2):
    return f"{lif(b1, b2, false())}"
def lor(b1, b2):
    return f"{lif(b1, true(), b2)}"
def xor(b1, b2):
    return f"{lif(b1, lnot(b2), b2)}"

def pair(x, y):
    return f"lambda _f : (_f ({x}) ({y}))"
def first(x):
    return f"{x} ({true()})"
def second(x):
    return f"{x} ({false()})"

# c = church numeral
def czero():
    return "lambda _f : lambda _x : _x"
def csucc(n):
    return f"lambda _f : lambda _x : (_f ({n} (_f) (_x)))"
def cplus(n, m):
    return f"{app2(n, csucc, m)}"
def cmult(n, m):
    return f"lambda _f : ({n} ({m} (_f)))"
def cexp(b, e):
    return f"{e} ({b})"
def ctwo():
    return f"{csucc(csucc(czero()))}"

def appfirst(f, p):
    return f"{pair(app(f, first(p)), second(p))}"
def appsecond(f, p):
    return f"{pair(first(p), app(f, second(p)))}"

# This is an _unusual_ representation
def zero():
    return f"{pair(czero(), czero())}"
def succ(n):
    return f"{appfirst(csucc, n)}"
def pred(n):
    return f"{appsecond(csucc, n)}"
def one():
    return f"{succ(zero())}"
def two():
    return f"{succ(one())}"

def neg(n):
    return f"{pair(second(n), first(n))}"
def plus(n, m):
    return f"{pair(app2(cplus, first(n), first(m)), app2(cplus, second(n), second(m)))}"
def minus(n, m):
    return f"{pair(app2(cplus, first(n), second(m)), app2(cplus, second(n), first(m)))}"
def mult(n, m):
    return f"{pair(app2(cplus, app2(cmult, first(n), first(m)), app2(cmult, second(n), second(m))), app2(cplus, app2(cmult, first(n), second(m)), app2(cmult, second(n), first(m))))}"

def ciszero(n):
    return f"{n} (lambda _x : {false()}) ({true()})"
# re: https://en.wikipedia.org/wiki/Lambda_calculus#Pairs
def cphi(x):
    return f"{pair(second(x), csucc(second(x)))}"
# be careful that cpred(0) = 0
def cpred(n):
    return f"{first(app2(n, cphi, pair(czero(), czero())))}"
def csub(n, m):
    return f"{app2(m, cpred, n)}"

def cleq(n, m):
    return f"{ciszero(csub(n, m))}"
def ceq(n, m):
    return f"{land(cleq(n, m), cleq(m, n))}"
def clt(n, m):
    return f"{land(cleq(n, m), lnot(cleq(m, n)))}"

def eq(n, m): #ALGEBRA
    return f"{ceq(cplus(first(n), second(m)), cplus(second(n), first(m)))}"
def leq(n, m):
    return f"{cleq(cplus(first(n), second(m)), cplus(second(n), first(m)))}"
def geq(n, m):
    return f"{leq(m, n)}"
def lt(n, m):
    return f"{land(leq(n, m), lnot(eq(n, m)))}"
def gt(n, m):
    return f"{lt(m, n)}"

# useful utility function that collapses an integer into the minimal positive or negative result
def collapse(n):
    return f"{lif(clt(second(n), first(n)), csub(first(n), second(n)), csub(second(n), first(n)))}"

# We use the z combinator cause eager Python evaluation
# Whenever you apply z, wrap the application in a 'lambda:', as usual
def z(rec):
    return f"(lambda _x : {rec} (lambda _v : _x (_x) (_v))) (lambda _x : {rec} (lambda _v : _x (_x) (_v)))"
# If you use an emit_runtime error, wrap the alternative in a thunk
def cdiv(n, m):
    return f"({lif(ciszero(m), emit_runtime_error_thunk('Divide by zero'), thunk('('+lif(clt(n, m), thunk(czero()), '(lambda:'+csucc(app2('_rec', csub(n, m), m))+')'))+')()')})()"
def cmod(n, m):
    return f"({lif(ciszero(m), emit_runtime_error_thunk('Mod by zero'), thunk('('+lif(clt(n, m), thunk(n), '(lambda:'+app2('_rec', csub(n, m), m)+')'))+')()')})()"

def div(n, m):
    return f"{lif(xor(clt(second(n), first(n)), clt(second(m), first(m))), pair(czero(), cdiv(collapse(n), collapse(m))), pair(cdiv(collapse(n), collapse(m)), czero()))}"
def mod(n, m):
    return f"({lif(lor(clt(first(n), second(n)), clt(first(m), second(m))), emit_runtime_error_thunk('Mod not permitted with negatives'), thunk(pair(cmod(collapse(n), collapse(m)), czero())))})()"
# If exponent is negative, error out
# otherwise compute exponent assuming positive base
# finally, if `n` is negative and `m` is a mod of 2, swap the two`
def exponent(n, m):
    return f"({lif(clt(first(m), second(m)), emit_runtime_error_thunk('Negative exponent not permitted'), thunk(lif(lor(cleq(second(n), first(n)), ciszero(cmod(collapse(m), ctwo()))), pair(cexp(collapse(n), collapse(m)), czero()), pair(czero(), cexp(collapse(n), collapse(m))))))})()"