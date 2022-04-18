from typing import List

class InternalException(Exception):
    def __init__(self, error : str):
        super().__init__("Internal error: " + str(error))

class UnimplementedException(InternalException):
    def __init__(self, value : any):
        super().__init__("Unimplemented " + str(value))

def typecheck(value : any, t : type) -> type:
    if not isinstance(value, t):
        raise InternalException("expected " + str(t.__name__) + " got " + str(value))
    return value
    
def typecheck_any(value : any, typs : List[type]):
    for t in typs:
        if isinstance(value, t):
            return
    raise InternalException("expected one of " + [str(t.__name__) for t in typs] + " got " + str(value))

class BaseClass:
    def __init__(self):
        raise Exception("Abstract class")
    def __repr__(self):
        raise InternalException("forgot to provide __repr__ to " + str(type(self)))