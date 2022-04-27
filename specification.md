# PyLambda Language Specification

## Overview

This document outlines the core syntax and language design of PyLambda.  How values are represented, some basic operations, and how control flow works are all specified here.  I would appreciate hearing about any ambiguity in this document in the issues!

All lambda calculus definitions used can be inspected by looking at the boilerplate definitions emitted with the `--debug` flag.  They are also defined in reasonably nice syntax in [src\lc_defs\lc_defs.py](https://github.com/Checkmate50/pylambda/blob/main/src/lc_defs/lc_defs.py), though note that this is not a "real" Python file.

## Syntax

The syntax of PyLambda is pretty much that of IMP (`examples` is the best reference for current syntax).  Internally, this syntax is separated into commands and expressions.  So, for example:

```
c := print e | input e | c1 ; c2 | ...
e := x | e1 + e2 | e1 ^ e2 | ...
```

Note that bitwise operations are nonsensical and so not supported, so `^` denotes exponentiation.  Note also that `e1 / e2` produces integer division currently, though real division is in the works at the time of writing.

## Type Interpretations (how it works)

There are two types of values supported in PyLambda: integers and booleans.  Since (ironically), you cannot currently define or use lambdas or functions in the PyLambda language, these are actually the full set of supported types along with the unit type for commands.  Values cannot be of the unit type, and expressions cannot operate over unit values syntactically.

### Booleans

Booleans are represented in the usual way to work with if-else expressions.  In particular, we define:

```
TRUE  := lambda x : lambda y : x
FALSE := lambda x : lambda y : y
```

We observe that if-then-else follows from these definitions somewhat trivially:

```
LIF := lambda b : lambda c1 : lambda c2 : b (c1) (c2)
```

Which in turn allows straightforward definitions of boolean operations:

```
NOT := lambda b : LIF (b) (false) (true)
OR  := lambda b1 : lambda b2 : LIF (b1) (true) (b2)
AND := lambda b1 : lambda b2 : LIF (b1) (b2) (false)
...
```

### Pairs

To define numbers, we first need the definition of _pairs_.  These will also be helpful when arrays are eventually included in the language.  Pairs are defined per [Wikipedia's definition](https://en.wikipedia.org/wiki/Lambda_calculus):

```
PAIR   := lambda x : lambda y : lambda f : f (x) (y)
FIRST  := lambda p : p (TRUE)
SECOND := lambda p : p (TRUE)
```

### Church Numerals

We use as a baseline for numbers the church numeral representation.  In particular, we define the following, where `C` denotes "Church":

```
C0 := lambda f : lambda x : x
C1 := lambda f : lambda x : f (x)
C2 := lambda f : lambda x : f (f (x))
```

We use the definitions given by the usual [Wikipedia article](https://en.wikipedia.org/wiki/Lambda_calculus) for operations.  All church operations are prepended with a `C` in PyLambda.

### Integers

PyLambda represents integers as pairs of church numerals `(a, b)`.  When interpreting these integers, we interpret `n := a - b`.  More precisely, for a given integer `n`, we print with the following Python interpretation:

```py
(FIRST(n) (lambda x : x + 1) (0)) - (SECOND(n) (lambda x : x + 1) (0))
```

This complicates our arithmetic operations somewhat.  Some are relatively simple, such as negation and addition:

```
NEG  := lambda (a, b) : (b, a)
PLUS := lambda (a, b) : lambda (c, d) : (a + c, b + d)
```

Which can be written in the lambda calculus as follows:

```
NEG  := lambda n : PAIR (SECOND (n)) (FIRST (n))
PLUS := lambda n : lambda m : PAIR (CPLUS (FIRST (n)) (FIRST (m))) (CPLUS (SECOND (n)) (SECOND (m)))
```

Multiplication, division, and exponentiation are more complicated.  They will not be written out here, but to give a sense of how this might work, multiplication is defined as follows:

```
MULT := lambda (a, b) : lambda (c, d) : (a * c + b * d, a * d + b * c)
```

Finally, comparison operations with integers are fairly complicated.  We use the well-known principle of church LEQ as a baseline, but we need to extend this to pairs.  This is done with the helper function COLLAPSE, which returns `if a <= b then b-a else a-b`.  This allows us to define LEQ, for example:

```
LEQ := lambda (a, b) : lambda (c, d) : if a <= b and c <= d then COLLAPSE(a, b) <= COLLAPSE(c, d) else ...
```

## Control Flow

Finally, the last bit of magic we do in PyLambda is allowing control flow.  This is done with multiple lines in Python code (though an intended feature is one-liners at some point) via declaring and using Python functions.  Note that using `if` and `while` statements _in Python_ would fundamentally defeat PyLambda's goal of being as silly as possible, so they are avoided.  In particular, we use a boilerplate class for scope along with some function semantic magic to get the intended if/while behavior:

```
IF    := lambda b : lambda c : LIF (b) (c()) (())
WHILE := lambda b : lambda c : Z(lambda rec : LIF (b) (rec(c())) (()))
```

Note that we both use the unit value here `()` since commands can't be changed and the Z-combinator, as usually defined.  We use the Z-combinator instead of the Y-combinator since Python has greedy lambda evaluation.

The last trick we do is for emitting If/Elif/Else chains, which basically is more of a compiler trick than a lambda calculus trick.  If/Elif/Else chains must be Seqs of each other in the PyLambda AST, which means that we can look ahead and replace the `else` condition of the `IF` definition with the appropriate follow-up.  This can, of course, be chained indefinitely.