from typing import TypeVar, Iterable
from heapq import heapify

from zpy.classes.collections.graph.complete_binary_tree import CompleteBinaryTree
from zpy.operators import identity

T = TypeVar("T")


class Heap(CompleteBinaryTree[T]):
    def __new__(cls, iter_: Iterable[T] = (), key=identity):
        self = super().__new__(cls, iter_)
        self.key = key
        self.stable_next = len(self)
        self.stable_order = list(range(len(self)))
        return self

    def cmp_value(self, idx: int):
        return self.key(self[idx]), self.stable_order[idx]

    def heapify(self):
        heapify(self, key=self.key)
