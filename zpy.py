from typing import Generic, TypeVar, Callable
from abc import abstractmethod, abstractclassmethod
from functools import reduce
from itertools import chain

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

_map = map
_filter = filter
_reduce = reduce
_pow = pow

def map(f: Callable[[T], U]) -> "Callable[[Functor[T]], Functor[U]]":
    return Function(lambda a: a.map(f))

def filter(f: Callable[[T], bool]) -> "Callable[[Functor[T]], Functor[T]]":
    return Function(lambda a: a.filter(f))

def reduce(i: U, f: Callable[[U, T], U]) -> "Callable[[Functor[T]], U]":
    return Function(lambda a: a.reduce(i, f))

def apply(f: "Applicative[Callable[[T], U]]") -> "Callable[[Applicative[T], Applicative[U]]":
    return Function(lambda a: a.apply(f))
    
foldl = reduce

def compose(*f):
    return Array(f).reduce(identity, Function(lambda f, g: Function(lambda x: f(g(x)))))

def pipe(*f):
    return compose(*reversed(f))

class Functor(Generic[T]):
    @abstractmethod
    def map(self, f: Callable[[T], U]) -> "Functor[U]":
        ...
        
class Applicative(Functor[T]):
    @classmethod
    @abstractmethod
    def pure(cls, m: T) -> "Applicative[T]":
        ...

    @abstractmethod
    def apply(self, f: "Functor[Callable[[T], U]]") -> "Applicative[U]":
        ...
        
    def map(self, f: Callable[[T], U]) -> "Applicative[U]":
        return apply(type(self).pure(f))(self)
    

class Function(Applicative[T], Generic[T, U]):
    def __init__(self, f: Callable[[T], U]):
        self.f = f
        
    def __call__(self, x: T, *rest) -> U:
        return self.f(x, *rest)
    
    @classmethod
    def pure(cls, m: U) -> "Function[Any, U]":
        return cls(const(m))

    def map(self, f: Callable[[U], V]) -> "Function[T, V]":
        return type(self)(compose(f, self))
        
    def apply(self, ft: "Functor[[Callable[U, V]]]") -> "Function[T, V]":
        return type(self)(lambda x: ft.map(type(self)(lambda f: f(x))))

class Array(Applicative[T], list):
    @classmethod
    def pure(cls, m: T) -> "Array[T]":
        return cls([m])
        
    @classmethod
    def of(cls, *args):
        return cls(args)

    def map(self, f: Callable[[T], U]) -> "Array[U]":
        return type(self)(_map(f, self))
    
    def reduce(self, i: U, f: Callable[[U, T], U]) -> U:
        return _reduce(f, self, i)

    def apply(self, ft: "Functor[T]") -> "Array[U]":
        return self.reduce(Array(), lambda a, fb: Array(chain(a, ft.map(lambda t: fb(t)))))
        
    def __repr__(self):
        return f"{type(self).__name__}({super().__repr__()})"


@Function
def identity(a: T) -> T:
    return a

@Function
def const(a: T) -> Callable[["Any"], T]:
    return Function(lambda _: a)

@Function
def fork(join):
    return Function(lambda f: lambda g: lambda x: join(f(x))(g(x)))

@Function
def tap(opr):
    return Function(lambda x: fork(const)(identity)(opr)(x))

@Function
def trace(x):
    print(x)
    


add = Function(lambda a: Function(lambda b: a + b))
sub = Function(lambda a: Function(lambda b: a - b))
mul = Function(lambda a: Function(lambda b: a * b))
pow = Function(lambda a: Function(lambda b: _pow(a, b)))
        


a = Array.pure(1)
add_1 = Function(add(1))
mul_4 = Function(mul(4))

print(map(add_1)(Array.of(2)))
print(apply()))
