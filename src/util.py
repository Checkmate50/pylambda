class InternalException(Exception):
    def __init__(self, error : str):
        super().__init__("Internal error: " + str(error))

def typecheck(value : any, t : type):
    if not isinstance(value, t):
        raise InternalException("expected " + str(t.__name__) + " got " + str(value))

class AbstractClass:
    def __init__(self):
        raise Exception("Abstract class")
    def __str__(self):
        raise InternalException("forgot to provide __str__ to " + str(type(self)))
    def __repr__(self):
        return self.__str__()