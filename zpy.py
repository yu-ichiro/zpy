from typing import TypeVar, Callable, Any, Iterable, Iterator, Tuple, cast
from abc import abstractmethod, ABC
from itertools import chain

from zpy.bases import Applicative, Cartesian, Functor
from zpy.operators import add, mul

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class Array(Applicative[T], Cartesian[T], list):
    @classmethod
    def pure(cls, m: T) -> "Array[T]":
        return cls([m])
        
    @classmethod
    def of(cls, *args):
        return cls(args)

    def map(self, f: Callable[[T], U]) -> "Array[U]":
        cls = type(self)
        return cls(_map(f, self))
    
    def product(self, f: "Array[U]") -> "Array[Tuple[T, U]]":
        cls = type(self)
        return cls(cast(Array[Tuple[T, U]], _product(self, f)))

    def reduce(self, i: U, f: Callable[[U, T], U]) -> U:
        return _reduce(f, self, i)

    def apply(self, ft: "Functor[U]") -> "Array[U]":
        return self.reduce(Array(), lambda a, f: Array(chain(a, ft.map(lambda t: f(t)))))
        
    def __repr__(self):
        return f"{type(self).__name__}({super().__repr__()})"


class Maybe(Applicative[T], Iterable[T], ABC):
    @abstractmethod
    def map(self, f: Callable[[T], U]) -> "Maybe[U]":
        ...

    @abstractmethod
    def apply(self, ff: "Maybe[Callable[[T], U]]") -> "Callable[[Maybe[T]], Maybe[U]]":
        ...

    @classmethod
    def pure(cls, m: T) -> "Maybe[T]":
        return Just(m)

    @classmethod
    def of(cls, m: T) -> "Maybe[T]":
        return cls.pure(m)


class Just(Maybe[T]):
    def __init__(self, m: T):
        self.m = m

    @classmethod
    def pure(cls, m: T) -> "Just[T]":
        return cls(m)

    @classmethod
    def of(cls, m: T, *_args) -> "Just[T]":
        return cls.pure(m)

    def __iter__(self) -> Iterator[T]:
        return iter([self.m])

    def map(self, f: Callable[[T], U]) -> "Just[U]":
        cls = type(self)
        return cls(f(self.m))

    def apply(self, f: "Just[U]") -> "Just[V]":
        cls = type(self)
        return cls(f.map(self.m))

    def __repr__(self):
        cls = type(self)
        return f"{cls.__name__}({repr(self.m)})"


class Nothing(Maybe[Any]):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance:
            return cls.__instance
        cls.__instance = super().__init__()

    @classmethod
    def pure(cls, _m: T) -> "Nothing":
        return cls()

    def __iter__(self) -> Iterator[Any]:
        return iter([])

    def map(self, _f: Callable[[Any], Any]) -> "Nothing":
        return self

    def apply(self, ff: "Apply[Callable[[T], U]]") -> "Nothing":
        return self

    def __repr__(self):
        return "Nothing()"


if __name__ == "__main__":
    a = Array.pure(1)
    add_1 = add(1)
    mul_4 = mul(4)

    # print(Array.pure(add).apply(Array.of(1, 2)).apply(Array.of(1)))
    # print(Just(1).map(add))
    # print(Just.pure(add).apply(Just(1)))
    print(add)
    print(add_1)
