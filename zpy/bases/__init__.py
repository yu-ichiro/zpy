from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Callable, Tuple

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class Functor(Generic[T], ABC):
    @abstractmethod
    def map(self, f: Callable[[T], U]) -> "Functor[U]":
        ...


class Cartesian(Generic[T], ABC):
    @abstractmethod
    def product(self, f: "Cartesian[U]") -> "Cartesian[Tuple[T, U]]":
        ...


class Apply(Functor[T], ABC):
    @abstractmethod
    def map(self, f: Callable[[T], U]) -> "Apply[U]":
        ...

    # def product(self, f: "Apply[U]") -> "Apply[Tuple[T, U]]":
    #     return apply

    @abstractmethod
    def apply(self: "Apply[Callable[[T], U]]", fa: "Apply[T]") -> "Apply[U]":
        ...


class Applicative(Apply[T], ABC):
    @abstractmethod
    def map(self, f: Callable[[T], U]) -> "Applicative[U]":
        ...

    # @abstractmethod
    # def product(self, f: "Applicative[U]") -> "Applicative[Tuple[T, U]]":
    #     ...

    @abstractmethod
    def apply(self, ff: "Applicative[Callable[[T], U]]") -> "Callable[[Applicative[T]], Applicative[U]]":
        ...

    @classmethod
    @abstractmethod
    def pure(cls, m: T) -> "Applicative[T]":
        ...


