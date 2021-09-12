from typing import TypeVar

from zpy.classes.bases.tree import Tree
from zpy.classes.collections.array import Array
from zpy.classes.logical.maybe import Maybe, Nothing, Just


T = TypeVar("T")


class CompleteBinaryTree(Array[T], Tree[T]):
    def root_idx(self) -> int:
        return 0

    def parent_idx(self, idx: int) -> int:
        if idx == 0:
            raise IndexError("no parent for root")
        return (idx + 1) // 2 - 1

    def children_idx(self, idx: int) -> Array[int]:
        return Array.of(
            2 * idx + 1,
            2 * idx + 2
        )

    def root(self) -> Maybe[T]:
        return self.get(self.root_idx())

    def parent(self, idx: int) -> Maybe[T]:
        if idx == 0:
            return Nothing()
        return self.get(self.parent_idx(idx))

    def children(self, idx: int) -> Array[T]:
        return self.children_idx(idx).flat_map(self.get)

    def sibling(self, idx: int) -> Maybe[T]:
        if idx == 0:
            return Nothing()
        if idx % 2 == 0:
            return Just(self[idx - 1])
        if idx == len(self) - 1:
            return Nothing()
        return Just(self[idx + 1])
