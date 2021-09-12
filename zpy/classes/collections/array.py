from itertools import chain
from typing import Iterable, Callable, cast, Tuple, TypeVar

from zpy.classes.bases import Applicative, Cartesian
from zpy.operators import builtin_map, builtin_product, builtin_reduce

T = TypeVar("T")
U = TypeVar("U")


_empty = object()


class Array(Applicative[T], Cartesian[T], list):
    def __new__(cls, iter_: Iterable[T] = _empty):
        if iter_ is _empty:
            return list.__new__(cls)
        return list.__new__(cls, iter_)

    @classmethod
    def pure(cls, m: T) -> "Array[T]":
        return cls([m])

    @classmethod
    def of(cls, *args):
        return cls(args)

    def map(self, f: Callable[[T], U]) -> "Array[U]":
        cls = type(self)
        return cls(builtin_map(f, self))

    def product(self, f: "Array[U]") -> "Array[Tuple[T, U]]":
        cls = type(self)
        return cls(cast(Array[Tuple[T, U]], builtin_product(self, f)))

    def reduce(self, i: U, f: Callable[[U, T], U]) -> U:
        return builtin_reduce(f, self, i)

    def apply(self: "Array[Callable[[T], U]]", ft: "Array[T]") -> "Array[U]":
        return self.reduce(Array(), lambda a, f: Array(chain(a, ft.map(lambda t: f(t)))))

    def __repr__(self):
        return f"{type(self).__name__}({super().__repr__()})"