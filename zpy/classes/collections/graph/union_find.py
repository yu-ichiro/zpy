from collections import defaultdict
from itertools import repeat
from typing import TypeVar, Iterable

from zpy.classes.bases.tree import Forest, Tree
from zpy.classes.collections.array import Array
from zpy.classes.logical.maybe import Maybe, Nothing, Just

T = TypeVar("T")


class UnionFind(Forest[T]):
    class _UnionFindTree(Tree[T]):
        def root(self) -> Maybe[T]:
            return Just(self._root_idx)

        def parent(self, idx: int) -> Maybe[T]:
            parent_idx = self.uf._uf[idx]
            if parent_idx < 0:
                return Nothing()
            return Just(parent_idx)

        def children(self, idx: int) -> Array[T]:
            if idx not in self.children_dict:
                return Array()
            return self.children_dict[idx]

        def root_idx(self) -> int:
            return self._root_idx

        def parent_idx(self, idx: int) -> int:
            parent_idx = self.uf._uf[idx]
            if parent_idx < 0:
                raise IndexError("No parent")
            return parent_idx

        def children_idx(self, idx: int) -> Array[int]:
            return self.children(idx)

        def get(self, idx: int) -> Maybe[T]:
            if 0 <= idx < self.uf.n:
                return Just(idx)
            return Nothing()

        def __getitem__(self, idx: int) -> T:
            return idx

        def __init__(self, uf: "UnionFind[T]", root: int):
            self._root_idx = root
            self.uf = uf
            self.children_dict = defaultdict(Array)
            for idx, link in enumerate(self.uf._uf):
                self.children_dict[link].append(idx)

    def __init__(self, n):
        self.n = n
        self._uf = Array(repeat(-1, times=self.n))
        self._ranks = Array(repeat(1, times=self.n))
        self._cached = set()
        self._trees = {}
        self.roots = set(range(self.n))

    def root(self, x):
        if self._uf[x] < 0:
            return x
        return self.root(self._uf[x])

    def flatten(self):
        for idx in range(self.n):
            root = self.root(idx)
            if root != idx:
                self._uf[idx] = root
        self._trees = {}
        self._cached = set()

    def rank(self, x):
        return self._ranks[self.root(x)]

    def size(self, x):
        return -self._uf[self.root(x)]

    def same(self, x, y):
        return self.root(x) == self.root(y)

    def unite(self, x, y):
        x, y = map(self.root, (x, y))
        if x == y:
            return
        rank_x, rank_y = map(self.rank, (x, y))
        if rank_x < rank_y:
            x, y = y, x
            rank_x, rank_y = rank_y, rank_x
        self._uf[x] += self._uf[y]
        self._uf[y] = x
        self.roots.remove(y)
        if x in self._cached:
            self._cached.remove(x)
        if y in self._cached:
            self._cached.remove(y)
        if y in self._trees:
            self._trees.pop(y)
        if rank_x == rank_y:
            self._ranks[x] += 1

    def trees(self) -> Iterable[Tree[T]]:
        roots_to_build = self.roots - self._cached
        for root in roots_to_build:
            self._trees[root] = self._UnionFindTree(self, root)
            self._cached.add(root)
        return Array(map(lambda r: self._trees[r], self.roots))

    def __repr__(self):
        cls = type(self)
        return f"{cls.__name__}({self.n})"
