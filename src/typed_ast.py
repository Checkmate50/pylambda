import src.util as util
import src.ast as ast
from typing import Generic, TypeVar

class BaseType(util.BaseClass):
    pass

class BoolType(BaseType):
    def __init__(self):
        pass
    def __repr__(self):
        return "tBool"

class IntType(BaseType):
    def __init__(self):
        pass
    def __repr__(self):
        return "tInt"

class UnitType(BaseType):
    def __init__(self):
        pass
    def __repr__(self):
        return "tUnit"

T = TypeVar('T')

class Typed(Generic[T]):
    def __init__(self, element : T, t : BaseType):
        util.typecheck(t, BaseType)

        self.element = element
        self.t = t
    def __repr__(self):
        return str(self.t) + " : " + str(self.element)