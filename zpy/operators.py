from inspect import Signature, Parameter
from itertools import product
from functools import reduce
from typing import Callable, TypeVar, Any

from zpy.bases import Functor
from zpy.function import Function
import operator as op

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")


_map = map
_filter = filter
_reduce = reduce
_pow = pow
_product = product


@Function
def map(f: Callable[[T], U]) -> "Callable[[Functor[T]], Functor[U]]":
    return Function(lambda a: a.map(f))


@Function
def filter(f: Callable[[T], bool]) -> "Callable[[Functor[T]], Functor[T]]":
    return Function(lambda a: a.filter(f))


@Function
def reduce(i: U, f: Callable[[U, T], U]) -> "Callable[[Functor[T]], U]":
    return Function(lambda a: a.reduce(i, f))


@Function
def apply(f: "Applicative[Callable[[T], U]]") -> "Callable[[Applicative[T]], Applicative[U]]":
    return Function(lambda a: a.apply(f))


@Function
def product(f: "Cartesian[U]") -> "Callable[[Cartesian[T]], Cartesian[Tuple[T, U]]]":
    return Function(lambda a: a.product(f))


fold_left = reduce
lift_a = apply


@Function
def compose(*f):
    if not f:
        return identity
    return f[0](compose(*f[1:]))


@Function
def pipe(*f):
    return compose(*reversed(f))


@Function
def identity(a: T) -> T:
    return a


@Function
def const(a: T) -> Callable[["Any"], T]:
    return Function(lambda _: a)


@Function
def fork(join, f, g, x):
    return join(f(x))(g(x))


@Function
def tap(opr):
    return Function(lambda x: fork(const)(identity)(opr)(x))


@Function
def trace(x):
    print(x)


__all__ = ['abs', 'add', 'and_', 'attrgetter', 'concat', 'contains', 'countOf',
           'delitem', 'eq', 'floordiv', 'ge', 'getitem', 'gt', 'iadd', 'iand',
           'iconcat', 'ifloordiv', 'ilshift', 'imatmul', 'imod', 'imul',
           'index', 'indexOf', 'inv', 'invert', 'ior', 'ipow', 'irshift',
           'is_', 'is_not', 'isub', 'itemgetter', 'itruediv', 'ixor', 'le',
           'length_hint', 'lshift', 'lt', 'matmul', 'methodcaller', 'mod',
           'mul', 'ne', 'neg', 'not_', 'or_', 'pos', 'pow', 'rshift',
           'setitem', 'sub', 'truediv', 'truth', 'xor']

# unary operator
# math
abs = Function(op.abs)
neg = Function(op.neg)
pos = Function(op.pos)
index = Function(op.index)

# bit
inv = Function(op.inv)
invert = inv

# boolean
not_ = Function(op.not_)
truth = Function(op.truth)

# binary operator
# math
add = Function(op.add)
sub = Function(op.sub)
mul = Function(op.mul)
truediv = Function(op.truediv)
floordiv = Function(op.floordiv)
mod = Function(op.mod)
matmul = Function(op.matmul)
divmod = Function(divmod)
pow = Function(_pow)

iadd = Function(op.iadd)
isub = Function(op.isub)
imul = Function(op.imul)
itruediv = Function(op.itruediv)
ifloordiv = Function(op.ifloordiv)
imod = Function(op.imod)
imatmul = Function(op.imatmul)
ipow = Function(op.ipow)

# bit
or_ = Function(op.or_)
and_ = Function(op.and_)
xor = Function(op.xor)
rshift = Function(op.rshift)
lshift = Function(op.lshift)

ior = Function(op.ior)
iand = Function(op.iand)
ixor = Function(op.ixor)
irshift = Function(op.irshift)
ilshift = Function(op.ilshift)

# boolean
eq = Function(op.eq)
ne = Function(op.ne)
gt = Function(op.gt)
ge = Function(op.ge)
lt = Function(op.lt)
le = Function(op.le)
is_ = Function(op.is_)
is_not = Function(op.is_not)

# object operator
itemgetter = Function(
    op.itemgetter,
    signature_=Signature([
        Parameter(name="items", kind=Parameter.VAR_POSITIONAL, annotation=str)
    ])
)
attrgetter = Function(
    op.attrgetter,
    signature_=Signature([
        Parameter(name="attrs", kind=Parameter.VAR_POSITIONAL, annotation=str)
    ])
)
methodcaller = Function(
    op.methodcaller,
    signature_=Signature([
        Parameter(name="__name", kind=Parameter.POSITIONAL_ONLY, annotation=str),
        Parameter(name="args", kind=Parameter.VAR_POSITIONAL, annotation=Any),
        Parameter(name="kwargs", kind=Parameter.VAR_KEYWORD, annotation=Any),
    ])
)

# sequence operator
getitem = Function(op.getitem)
setitem = Function(op.setitem)
delitem = Function(op.delitem)
indexOf = Function(op.indexOf)
concat = Function(op.concat)
contains = Function(op.contains)
count_of = Function(op.countOf)
countOf = count_of
length_hint = Function(op.length_hint)

iconcat = Function(op.iconcat)
