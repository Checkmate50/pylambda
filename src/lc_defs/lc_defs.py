"""
So basically this is a meta-file to be used by lc_constants_macro
We make it a py file for linting, but this file alone will not do what we want
"""

def false():
    return "lambda x : lambda y : y"
def true():
    return "lambda x : lambda y : x"

def app(x, y):
    return f"{x} ({y})"
def pair(x, y):
    return f"lambda f : (f ({x}) ({y}))"
def first(x):
    return f"{x} ({true()})"
def second(x):
    return f"{x} ({false()})"

# This is an _unusual_ representation
def czero():
    return "lambda f : lambda x : x"
def zero():
    return f"{pair(czero(), czero())}"
def csucc(n):
    return f"lambda f : lambda x : (f ({n} (f) (x)))"
def cplus(m, n):
    return f"{m} ({csucc}) ({n})"
def cmult(m, n):
    return f"lambda f : ({m} ({n} (f)))"
def cexp_def(b, e):
    return f"{e} ({b})"

def appfirst(f, p):
    return f"{pair(app(f, first(p)), second(p))}"
def appsecond(f, p):
    return f"{pair(first(p), app(f, second(p)))}"
def appboth(f, p):
    return f"{pair(app(f, first(p)), app(f, second(p)))}"

def succ(n):
    return f"{appfirst(csucc, n)}"
def pred(n):
    return f"{appsecond(csucc, n)}"
def one():
    return f"{succ(zero())}"
# def plus(n, m) -> str:
#     return f"{appboth(cplus, )}"