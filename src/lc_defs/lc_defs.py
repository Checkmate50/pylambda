"""
So basically this is a meta-file to be used by lc_constants_macro
We make it a py file for linting, but this file alone will not do what we want
"""

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

def app(x, y):
    return f"{x} ({y})"
def app2(x, y, z):
    return f"{x} ({y}) ({z})"
def pair(x, y):
    return f"lambda _f : (_f ({x}) ({y}))"
def first(x):
    return f"{x} ({true()})"
def second(x):
    return f"{x} ({false()})"

# This is an _unusual_ representation
def czero():
    return "lambda _f : lambda _x : _x"
def zero():
    return f"{pair(czero(), czero())}"
def csucc(n):
    return f"lambda _f : lambda _x : (_f ({n} (_f) (_x)))"
def cplus(m, n):
    return f"{m} ({csucc}) ({n})"
def cmult(m, n):
    return f"lambda _f : ({m} ({n} (_f)))"
def cexp_def(b, e):
    return f"{e} ({b})"

def appfirst(f, p):
    return f"{pair(app(f, first(p)), second(p))}"
def appsecond(f, p):
    return f"{pair(first(p), app(f, second(p)))}"

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

# We use the z combinator cause eager Python evaluation
def z(f):
    return f"(lambda _x : {f} (lambda _v : _x (_x) (_v))) (lambda _x : _f (lambda _v : _x (_x) (_v)))"
def iszero(n):
    return f"{first(n)} (lambda _x : lambda _a : lambda _b : _b) (lambda _x : lambda _y : _x)"