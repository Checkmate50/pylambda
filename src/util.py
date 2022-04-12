class InternalException(Exception):
    def __init__(self, error : str):
        super().__init__("Internal error: " + str(error))

def typecheck(value : any, t : type):
    if not isinstance(value, t):
        raise InternalException("expected " + str(t.__name__) + " got " + str(value))

class BaseClass:
    def __init__(self):
        raise Exception("Abstract class")
    def __repr__(self):
        raise InternalException("forgot to provide __repr__ to " + str(type(self)))