import inspect

FALSE = lambda x : lambda y : y
TRUE = lambda x : lambda y : x
_func = TRUE
print(str(inspect.getsourcelines(_func)[0]).strip("['\\n']").split(" = ")[1])
_func = FALSE
print(str(inspect.getsourcelines(_func)[0]).strip("['\\n']").split(" = ")[1])
