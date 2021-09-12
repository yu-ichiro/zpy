from typing import TypeVar

from zpy.classes.collections.array import Array
from zpy.classes.logical.maybe import Just
from zpy.operators import add, mul, apply

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")

if __name__ == "__main__":
    a = Array.pure(1)
    add_1 = add(1)
    mul_4 = mul(4)

    # print(Array.pure(add).apply(Array.of(1, 2)).apply(Array.of(1)))
    # print(Just(1).map(add))
    # print(Just.pure(add).apply(Just(1)))
    print(Just.pure(add).apply(Just(1)).apply(Just(3)))
    print(Just(1).map(add).apply(Just(3)))
    print(apply(apply(Just(add))(Just(3)))(Just(1)))
    print(add_1 / Just(1))
    print(mul_4 / Just(5))
    print(add_1 / mul_4 / Just(5))
    print(add / Just(3) * Just(5))
    print(Just(add) * Just(3) * Just(5))
    print(add / Array.of(1, 2, 3) * Array.of(3, 6))
