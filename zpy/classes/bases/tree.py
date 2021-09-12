from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from enum import IntFlag
from typing import Generic, Callable, List, TypeVar

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

    def bfs(self, action: Callable[[TraverseState[T]], bool] = const(True)):
        if not self.root():
            return
        root = self.root_idx()
        queue = deque([root])
        depth_queue = deque([0])
        while queue:
            current = queue.popleft()
            depth = depth_queue.popleft()
            state = TraverseState(index=current, item=self[current], depth=depth)
            if not action(state):
                break
            for child in self.children_idx(current):
                if not self.get(child):
                    continue
                queue.append(child)
                depth_queue.append(depth + 1)

    def dfs(self, action: Callable[[TraverseState[T]], bool] = const(True)):
        if not self.root():
            return

        def traverse(idx: int, depth=0):
            state = TraverseState(index=idx, item=self[idx], depth=depth)
            if not action(state):
                return
            for child in self.children_idx(idx):
                if not self.get(child):
                    continue
                traverse(child, depth + 1)

        traverse(self.root_idx())

    def __pretty__(self):
        cols: List[List[str]] = []
        spaced_cols: List[List[str]] = []

        def action(state: TraverseState[T]):
            if state.depth == len(spaced_cols):
                cols.append([])
                spaced_cols.append([])
            cols[state.depth].append(repr(state.item))
            spaced_cols[state.depth].append(repr(state.item))
            if self.parent(state.index) and self.children_idx(self.parent_idx(state.index))[0] == state.index:
                return True
            for i in range(state.depth):
                spaced_cols[i].append("")
            return True

        self.dfs(action)
        if not cols:
            print()
            return
        spaced_cols[-1] = spaced_cols[-1] + [""] * (len(spaced_cols[0]) - len(spaced_cols[-1]))
        col_widths = [
            max(map(len, col))
            for col in spaced_cols
        ]
        count = [0 for _ in range(len(cols))]
        for y, row in enumerate(zip(*spaced_cols)):
            is_bottom_end = y == len(spaced_cols[0]) - 1
            for x, item in enumerate(row):
                is_left_end = x == 0
                is_right_end = x == len(spaced_cols) - 1
                has_left = not is_left_end and bool(spaced_cols[x-1][y])
                not_empty = bool(spaced_cols[x][y])
                if not is_left_end and count[x] < len(cols[x]):
                    bars = ""
                    should_corner = is_bottom_end or bool(spaced_cols[x-1][y+1]) or count[x] + 1 == len(cols[x])
                    if has_left and should_corner:
                        bars += "─"
                    elif has_left:
                        bars += "┬"
                    elif not_empty and not should_corner:
                        bars += "├"
                    elif not_empty and should_corner:
                        bars += "└"
                    else:
                        bars += "│"
                    if not_empty:
                        bars += "╴"
                    else:
                        bars += " "
                    print(bars, end="")
                elif not is_left_end:
                    print("  ", end="")
                print(f"{{:>{col_widths[x]}}}".format(item), end="")
                if not is_right_end and count[x+1] < len(cols[x+1]):
                    bars = ""
                    if not_empty:
                        bars += "╶"
                    else:
                        bars += " "
                    print(bars, end="")
                elif not is_right_end:
                    print(" ", end="")
                if not_empty:
                    count[x] += 1
            print()