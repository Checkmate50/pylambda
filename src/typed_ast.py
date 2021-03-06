import src.util as util
from typing import Generic, TypeVar

class BaseType(util.BaseClass):
    pass

class BoolType(BaseType):
    def __init__(self):
        pass
    def __repr__(self):
        return "type bool"

class IntType(BaseType):
    def __init__(self):
        pass
    def __repr__(self):
        return "type int"

class UnitType(BaseType):
    def __init__(self):
        pass
    def __repr__(self):
        return "type unit"

T = TypeVar('T')

class Typed(Generic[T]):
    def __init__(self, element : T, typ : BaseType):
        util.typecheck(typ, BaseType)

        self.element = element
        self.typ = typ
    def __repr__(self):
        return str(self.typ) + " : " + str(self.element)