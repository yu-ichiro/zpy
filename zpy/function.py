import re
import warnings
from collections import deque
from inspect import signature
from functools import partial
from typing import TypeVar, Callable, Any, Generic

from zpy.classes.bases import Functor

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


class Function(Functor[T]):
    def __new__(cls, f: Callable[[T], Any] = None, name=None, signature_=None, applied_args=None, applied_kwargs=None):
        if isinstance(f, Function):
            return f
        if not f:
            return partial(cls, name=name, signature_=signature_)
        return super().__new__(cls)

    def __init__(self, f: Callable[[T], Any] = None, name=None, signature_=None, applied_args=None, applied_kwargs=None):
        if isinstance(f, Function):
            return
        self.__doc__ = f.__doc__
        self.__name__ = name or f.__name__
        self.signature = signature_ or signature(f)
        self.applied_args = applied_args or []
        self.applied_kwargs = applied_kwargs or {}
        self.__applied_args = ""
        self.f = f
        self.__wrapped__ = f
        self.__signature__ = self.signature

    @property
    def __applied_args__(self):
        if self.__applied_args:
            return self.__applied_args
        if self.applied_args or self.applied_kwargs:
            str_args = [
                f"{value}"
                for value in self.applied_args
            ]
            str_kwargs = [
                f"{key}={value}"
                for key, value in self.applied_kwargs.items()
            ]
            self.__applied_args = f"({', '.join(str_args + str_kwargs)})"
        return self.__applied_args

    def __repr__(self):
        name = self.__name__ or type(self).__name__
        return f"{name}{self.__applied_args__}{self.signature}"

    def __call__(self, *args, **kwargs) -> U:
        cls = type(self)
        arguments = deque(args)
        kw_arguments = dict(**kwargs)
        parameters = deque(self.signature.parameters.values())

        apply_args = []
        apply_kwargs = {}
        missing_params = []
        exceeding_args = []
        exceeding_kwargs = {}
        while True:
            if not arguments and not kw_arguments and not parameters:
                break
            if (arguments or kw_arguments) and not parameters:
                exceeding_args.extend(arguments)
                exceeding_kwargs.update(kw_arguments)
                break
            param = parameters.popleft()
            if param.kind == param.POSITIONAL_ONLY:
                if not arguments:
                    if param.default is param.empty:
                        missing_params.append(param)
                    else:
                        apply_args.append(param.default)
                else:
                    apply_args.append(arguments.popleft())
            elif param.kind == param.KEYWORD_ONLY:
                if param.name not in kw_arguments:
                    if param.default is param.empty:
                        missing_params.append(param)
                    else:
                        apply_kwargs[param.name] = param.default
                else:
                    apply_kwargs[param.name] = kw_arguments.pop(param)
            elif param.kind == param.VAR_POSITIONAL:
                apply_args.extend(arguments)
                arguments.clear()
            elif param.kind == param.VAR_KEYWORD:
                apply_kwargs.update(kw_arguments)
                kw_arguments.clear()
            else:
                if arguments:
                    apply_args.append(arguments.popleft())
                elif param.name in kw_arguments:
                    apply_kwargs[param.name] = kw_arguments.pop(param.name)
                elif kw_arguments:
                    missing_params.append(param)
                else:
                    break

        if missing_params and exceeding_args:
            warnings.warn(RuntimeWarning(f"exceeding arguments {repr(exceeding_args)} are ignored"
                                         f" because keyword parameters {repr(missing_params)} are missing"))
        if missing_params and exceeding_kwargs:
            warnings.warn(RuntimeWarning(f"exceeding keyword arguments {repr(exceeding_kwargs)} are ignored"
                                         f" because parameters {repr(missing_params)} are missing"))

        if missing_params:
            return self.partial(*apply_args, **apply_kwargs)
        if exceeding_args or exceeding_kwargs:
            return self.f(*apply_args, **apply_kwargs)(*exceeding_args, **exceeding_kwargs)
        return self.f(*apply_args, **apply_kwargs)

    def partial(self, *args, **kwargs):
        cls = type(self)
        return cls(partial(self, *args, **kwargs), name=self.__name__, applied_args=args, applied_kwargs=kwargs)

    @classmethod
    def pure(cls, m: U) -> "Callable[[T], U]":
        return cls(lambda _x: m)

    def map(self: Callable[[T], U], f: Callable[[U], V]) -> Callable[[T], V]:
        f = Function(f)
        cls = type(self)
        return cls(
            lambda t: f(self(t)),
            name=f"{f.__name__}{f.__applied_args__} / {self.__name__}{self.__applied_args__}"
        )
        
    def __truediv__(self: Callable[[T], U], f: Callable[[V], T]) -> Callable[[V], U]:
        return type(f).__rtruediv__(f, self)

    def apply(self: Callable[[T], Callable[[U], V]], f: Callable[[T], U]) -> Callable[[T], V]:
        cls = type(self)
        return cls(lambda t: self(t)(f(t)))

    def __mul__(self: Callable[[T], U], f: Callable[[V], T]) -> Callable[[V], U]:
        f = Function(f)
        cls = type(self)
        return cls(
            lambda t: self(f(t)),
            name=f"{self.__name__}{self.__applied_args__} * {f.__name__}{f.__applied_args__}"
        )


class UnderBar:
    _instance = None
    pattern = re.compile(r"(?<![a-zA-Z0-9])_(?![a-zA-Z0-9])")

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return "_"


_ = UnderBar()


class When(Generic[T, U]):
    def __init__(self, m: Any, expr_func: Callable[[Any, ...], U]):
        self.m = re.compile(re.sub(UnderBar.pattern, r"(?<![a-zA-Z0-9])(.+)(?![a-zA-Z0-9])", repr(m)))
        self.f = Function(expr_func)

    def matches(self, pattern: str):
        return self.m.match(pattern)

    def __contains__(self, item: T):
        return self.matches(repr(item))


class Case(Generic[T, U]):
    def __init__(self, *patterns: When[T, U]):
        self.patterns = deque(patterns)
        self._cache = {}

    def append(self, pattern: When[T, U]):
        self.patterns.append(pattern)

    def prepend(self, pattern: When[T, U]):
        self.patterns.appendleft(pattern)

    def __call__(self, case: T) -> U:
        case_repr = repr(case)
        if case_repr not in self._cache:
            for pattern in self.patterns:
                if pattern.matches(case_repr):
                    self._cache[case_repr] = pattern.f(case)
                    break
            else:
                raise NotImplementedError(f"Unknown Case: {case}")
        return self._cache[case_repr]

    def __or__(self, other):
        if isinstance(other, When):
            self.append(other)
            return self
        return type(other).__ror__(other, self)
