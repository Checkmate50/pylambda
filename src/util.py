def typecheck(value : any, t : type):
    if not isinstance(value, t):
        raise Exception("Internal Error, expected " + str(t.__name__) + " got " + value)

class AbstractClass:
    def __init__(self):
        raise Exception("Abstract class")
    def __str__(self):
        raise Exception("Internal Error: forgot to __str__ an object")
    def __repr__(self):
        return self.__str__()