from typing import TypeVar, Iterable, Union
from heapq import heapify, heappop, heappush

from zpy.operators import identity
from zpy.classes.collections.array import Array


T = TypeVar("T")


class CompleteBinaryTree(Array[T]):
    def parent(self, idx: int):
        if idx == 0:
            return None


class Heap(Array[T]):
    def __new__(cls, iter_: Iterable[T], key=identity):
        self = super().__new__(cls, iter_)
        self.key = key
        self.stable_next = len(self)
        self.stable_order = list(range(len(self)))
        return self
        
    def cmp_value(self, idx: int):
        return self.key(self[idx]), self.stable_order[idx]
        
    
        
    def heapify(self):
        heapify(self, key=self.key)
    
