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


builtin_map = map
builtin_filter = filter
builtin_reduce = reduce
builtin_pow = pow
builtin_product = product


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
    return Function(lambda a: f.apply(a))


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


unary = Signature([
    Parameter(name="a", kind=Parameter.POSITIONAL_ONLY)
])
# unary operator
# math
abs = Function(op.abs, signature_=unary)
neg = Function(op.neg, signature_=unary)
pos = Function(op.pos, signature_=unary)
index = Function(op.index, signature_=unary)

# bit
inv = Function(op.inv, signature_=unary)
invert = inv

# boolean
not_ = Function(op.not_, signature_=unary)
truth = Function(op.truth, signature_=unary)

binary = Signature([
    Parameter(name="a", kind=Parameter.POSITIONAL_ONLY),
    Parameter(name="b", kind=Parameter.POSITIONAL_ONLY),
])
# binary operator
# math
add = Function(op.add, signature_=binary)
sub = Function(op.sub, signature_=binary)
mul = Function(op.mul, signature_=binary)
truediv = Function(op.truediv, signature_=binary)
floordiv = Function(op.floordiv, signature_=binary)
mod = Function(op.mod, signature_=binary)
matmul = Function(op.matmul, signature_=binary)
divmod = Function(divmod, signature_=binary)
pow = Function(builtin_pow)

iadd = Function(op.iadd, signature_=binary)
isub = Function(op.isub, signature_=binary)
imul = Function(op.imul, signature_=binary)
itruediv = Function(op.itruediv, signature_=binary)
ifloordiv = Function(op.ifloordiv, signature_=binary)
imod = Function(op.imod, signature_=binary)
imatmul = Function(op.imatmul, signature_=binary)
ipow = Function(op.ipow, signature_=binary)

# bit
or_ = Function(op.or_, signature_=binary)
and_ = Function(op.and_, signature_=binary)
xor = Function(op.xor, signature_=binary)
rshift = Function(op.rshift, signature_=binary)
lshift = Function(op.lshift, signature_=binary)

ior = Function(op.ior, signature_=binary)
iand = Function(op.iand, signature_=binary)
ixor = Function(op.ixor, signature_=binary)
irshift = Function(op.irshift, signature_=binary)
ilshift = Function(op.ilshift, signature_=binary)

# boolean
eq = Function(op.eq, signature_=binary)
ne = Function(op.ne, signature_=binary)
gt = Function(op.gt, signature_=binary)
ge = Function(op.ge, signature_=binary)
lt = Function(op.lt, signature_=binary)
le = Function(op.le, signature_=binary)
is_ = Function(op.is_, signature_=binary)
is_not = Function(op.is_not, signature_=binary)

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
getitem = Function(op.getitem, signature_=binary)
setitem = Function(op.setitem, signature_=binary)
delitem = Function(op.delitem, signature_=binary)
index_of = Function(op.indexOf, signature_=binary)
indexOf = index_of
concat = Function(op.concat, signature_=binary)
contains = Function(op.contains, signature_=binary)
count_of = Function(op.countOf, signature_=binary)
countOf = count_of
length_hint = Function(op.length_hint, signature_=binary)

iconcat = Function(op.iconcat, signature_=binary)
