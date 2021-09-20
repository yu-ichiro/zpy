from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from enum import IntFlag
from typing import Generic, Callable, List, TypeVar, Iterable

from zpy.classes.bases.utility.pretty import Pretty
from zpy.classes.collections.array import Array
from zpy.classes.logical.maybe import Maybe
from zpy.operators import const


T = TypeVar("T")


@dataclass
class TraverseState(Generic[T]):
    index: int
    item: T
    depth: int


class BoxPart(IntFlag):
    EMPTY = 0
    TOP = 1 << 0
    BOTTOM = 1 << 1
    LEFT = 1 << 2
    RIGHT = 1 << 3

    @property
    def box_map(self):
        cls = type(self)
        if not hasattr(cls, "_box_map"):
            setattr(cls, "_box_map", {
                cls.TOP: "╵",
                cls.BOTTOM: "╷",
                cls.LEFT: "╴",
                cls.RIGHT: "╶",
                cls.TOP | cls.LEFT: "┘",
                cls.TOP | cls.RIGHT: "└",
                cls.BOTTOM | cls.LEFT: "┐",
                cls.BOTTOM | cls.RIGHT: "┌",
                cls.LEFT | cls.RIGHT | cls.BOTTOM: "┬",
                cls.TOP | cls.LEFT | cls.RIGHT: "┴",
                cls.TOP | cls.RIGHT | cls.BOTTOM: "├",
                cls.TOP | cls.LEFT | cls.BOTTOM: "┤",
                cls.TOP | cls.BOTTOM: "│",
                cls.LEFT | cls.RIGHT: "─",
                cls.TOP | cls.LEFT | cls.RIGHT | cls.BOTTOM: "┼",
                0: " ",
            })
        return cls._box_map

    def __str__(self):
        return self.box_map[self]


class Tree(Generic[T], Pretty, ABC):
    @abstractmethod
    def root(self) -> Maybe[T]:
        ...

    @abstractmethod
    def parent(self, idx: int) -> Maybe[T]:
        ...

    @abstractmethod
    def children(self, idx: int) -> Array[T]:
        ...

    @abstractmethod
    def root_idx(self) -> int:
        ...

    @abstractmethod
    def parent_idx(self, idx: int) -> int:
        ...

    @abstractmethod
    def children_idx(self, idx: int) -> Array[int]:
        ...

    @abstractmethod
    def get(self, idx: int) -> Maybe[T]:
        ...

    @abstractmethod
    def __getitem__(self, idx: int) -> T:
        ...

    def bfs(self, check: Callable[[TraverseState[T]], bool] = const(True)):
        if not self.root():
            return
        root = self.root_idx()
        queue = deque([root])
        depth_queue = deque([0])
        while queue:
            current = queue.popleft()
            depth = depth_queue.popleft()
            state = TraverseState(index=current, item=self[current], depth=depth)
            if not check(state):
                return state
            for child in self.children_idx(current):
                if not self.get(child):
                    continue
                queue.append(child)
                depth_queue.append(depth + 1)

    def dfs(self, check: Callable[[TraverseState[T]], bool] = const(True)):
        if not self.root():
            return

        def traverse(idx: int, depth=0):
            state = TraverseState(index=idx, item=self[idx], depth=depth)
            if check(state):
                print(state)
                return state
            for child in self.children_idx(idx):
                if not self.get(child):
                    continue
                traverse(child, depth + 1)

        return traverse(self.root_idx())

    def __pretty__(self):
        cols: List[List[str]] = []
        edges: List[List[BoxPart]] = []

        def action(state: TraverseState[T]):
            if state.depth == len(cols):
                cols.append([])
            for _ in range(len(cols[state.depth]), len(cols[0])-1):
                cols[state.depth].append("")
            if state.depth - 1 == len(edges):
                edges.append([])
            if edges:
                for _ in range(len(edges[state.depth-1]), len(edges[0])-1):
                    edges[state.depth-1].append(BoxPart.EMPTY)
            cols[state.depth].append(repr(state.item))
            if self.parent(state.index):
                edges[state.depth - 1].append(BoxPart.RIGHT)
            if self.parent(state.index) and self.children_idx(self.parent_idx(state.index))[0] == state.index:
                edges[state.depth - 1][-1] |= BoxPart.LEFT
                return False
            elif self.parent(state.index):
                edges[state.depth - 1][-1] |= BoxPart.TOP
                edges_len = len(edges[state.depth - 1])
                for i in range(edges_len-2, -1, -1):
                    edges[state.depth - 1][i] |= BoxPart.BOTTOM
                    if edges[state.depth - 1][i] & BoxPart.LEFT:
                        break
                    else:
                        edges[state.depth - 1][i] |= BoxPart.TOP
            for i in range(state.depth):
                cols[i].append("")
            for i in range(state.depth-1):
                edges[i].append(BoxPart.EMPTY)
            return False

        self.dfs(action)
        if not cols:
            print()
            return
        for col in cols[1:]:
            col += [""] * (len(cols[0]) - len(col))
        for edge in edges:
            edge += [BoxPart.EMPTY] * (len(cols[0]) - len(edge))

        col_widths = [
            max(map(len, col))
            for col in cols
        ]
        result = ""
        for y, row in enumerate(zip(*cols)):
            for x, col in enumerate(row):
                if x > 0:
                    result += str(BoxPart.RIGHT if edges[x-1][y] & BoxPart.LEFT else BoxPart.EMPTY)
                    result += str(edges[x-1][y])
                    result += str(BoxPart.LEFT if edges[x - 1][y] & BoxPart.RIGHT else BoxPart.EMPTY)
                result += f"{{:>{col_widths[x]}}}".format(col)
            result += "\n"
        return result[:-1]


class Forest(Generic[T], Pretty, ABC):
    @abstractmethod
    def trees(self) -> Iterable[Tree[T]]:
        ...

    def __pretty__(self):
        return "\n".join(map(lambda tree: type(tree).__pretty__(tree), self.trees()))
