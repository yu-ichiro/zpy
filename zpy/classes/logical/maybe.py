from abc import ABC, abstractmethod
from typing import Iterable, Callable, Iterator, Any, TypeVar

from zpy.classes.bases import Applicative, Apply

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class Maybe(Applicative[T], Iterable[T], ABC):
    @abstractmethod
    def map(self, f: Callable[[T], U]) -> "Maybe[U]":
        ...

    @abstractmethod
    def apply(self, ff: "Maybe[Callable[[T], U]]") -> "Callable[[Maybe[T]], Maybe[U]]":
        ...

    @abstractmethod
    def unwrap(self) -> T:
        ...

    @abstractmethod
    def unwrap_or(self, else_: T) -> T:
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

    def apply(self, fa: "Just[U]") -> "Just[V]":
        cls = type(self)
        return fa.map(self.m)

    def unwrap(self) -> T:
        return self

    def unwrap_or(self, _else_: T) -> T:
        return self.unwrap()

    def __repr__(self):
        cls = type(self)
        return f"{cls.__name__}({repr(self.m)})"


class ForceUnwrapError(TypeError):
    pass


class Nothing(Maybe[Any]):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def pure(cls, _m: T) -> "Nothing":
        return cls()

    def __iter__(self) -> Iterator[Any]:
        return iter([])

    def map(self, _f: Callable[[Any], Any]) -> "Nothing":
        return self

    def apply(self, ff: Apply[Callable[[T], U]]) -> "Nothing":
        return self

    def unwrap(self) -> T:
        raise ForceUnwrapError("tried to unwrap nothing")

    def unwrap_or(self, else_: T) -> T:
        return else_

    def __bool__(self):
        return False

    def __repr__(self):
        return "Nothing()"
