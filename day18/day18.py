"""Day 18."""

from __future__ import annotations

import operator
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from functools import reduce
from itertools import permutations
from typing import Any

import utils.parser as pc
from result import Result


@dataclass
class ExplodeResult:
    """A class containing the results of an explode."""

    change_made: bool
    left_result: int | None = None
    right_result: int | None = None


class SnailfishNode(ABC):
    """Base class for all nodes in snailfish tree."""

    def __init__(self) -> None:
        """Initialize new snailfish node."""
        self.parent: SnailfishNumber | None = None

    @staticmethod
    def _parse_side(s: str, offset: int = 0) -> tuple[SnailfishNode, int]:
        """Parse one side of a snailfish number."""
        if s[offset] == "[":
            return SnailfishNode._parse_impl(s, offset)
        else:
            return SnailfishLeaf(int(s[offset])), offset + 1

    @staticmethod
    def _parse_impl(s: str, offset: int = 0) -> tuple[SnailfishNumber, int]:
        """Parse a snailfish number from a fragment of a string."""
        assert s[offset] == "["
        left, new_offset = SnailfishNode._parse_side(s, offset + 1)
        assert s[new_offset] == ","
        right, new_offset = SnailfishNode._parse_side(s, new_offset + 1)
        assert s[new_offset] == "]"
        return SnailfishNumber(left, right), new_offset + 1

    @staticmethod
    def from_string(s: str) -> SnailfishNumber:
        """Parse a Snailfish Number from a string."""
        result, new_offset = SnailfishNumber._parse_impl(s)
        assert new_offset == len(s)
        return result

    def replace_self(self, new_node: SnailfishNode) -> None:
        """Replace this node in the tree with a new node."""
        assert self.parent is not None
        if self.parent.left == self:
            self.parent.left = new_node
        else:
            self.parent.right = new_node

    @abstractmethod
    def find_left_leaf(self) -> SnailfishLeaf:
        """Find the leaf node on the far left of the tree."""

    @abstractmethod
    def find_right_leaf(self) -> SnailfishLeaf:
        """Find the leaf node on the far right of the tree."""

    @abstractmethod
    def split(self) -> bool:
        """Check for numbers above 9 and split them."""

    @property
    @abstractmethod
    def magnitude(self) -> int:
        """Compute the magnitude of the Snailfish Number."""


class SnailfishLeaf(SnailfishNode):
    """A class representing a leaf node of a Snailfish Number."""

    def __init__(self, value: int) -> None:
        """Create a new leaf node."""
        self.value = value
        super().__init__()

    def __str__(self) -> str:
        """Return string representation of the number."""
        return str(self.value)

    def find_left_leaf(self) -> SnailfishLeaf:
        """Find the leaf node on the far left the tree."""
        return self

    def find_right_leaf(self) -> SnailfishLeaf:
        """Find the leaf node on the far left the tree."""
        return self

    def split(self) -> bool:
        """Check for numbers above 9 and split them."""
        if self.value > 9:
            low_half = self.value // 2
            self.replace_self(
                SnailfishNumber(
                    SnailfishLeaf(low_half), SnailfishLeaf(self.value - low_half)
                )
            )
            return True
        return False

    @property
    def magnitude(self) -> int:
        """Compute the magnitude of the Snailfish Number."""
        return self.value


class SnailfishNumber(SnailfishNode):
    """A class representing a Snailfish Number."""

    def __init__(
        self,
        left: SnailfishNode,
        right: SnailfishNode,
    ) -> None:
        """Create a new number."""
        self.left = left
        self.right = right

        self.left.parent = self
        self.right.parent = self
        super().__init__()

    def __setattr__(self, name: str, value: Any) -> None:
        """Set the parent of a child if a new one is assigned."""
        if name in {"left", "right"}:
            assert isinstance(value, SnailfishNode)
            value.parent = self
        super().__setattr__(name, value)

    def __str__(self) -> str:
        """Return string representation of the number."""
        return f"[{self.left},{self.right}]"

    def __add__(self, other: SnailfishNumber) -> SnailfishNumber:
        """Add two Snailfish Numbers together."""
        result = SnailfishNumber(left=deepcopy(self), right=deepcopy(other))
        result.reduce()
        return result

    def find_left_leaf(self) -> SnailfishLeaf:
        """Find the leaf node on the far left the tree."""
        return self.left.find_left_leaf()

    def find_right_leaf(self) -> SnailfishLeaf:
        """Find the leaf node on the far left the tree."""
        return self.right.find_right_leaf()

    def explode(self, depth: int = 0) -> ExplodeResult:
        """Check and execute explosions in the Snailfish Number."""
        if depth == 4:
            # We should never pass depth 4...
            assert isinstance(self.left, SnailfishLeaf)
            assert isinstance(self.right, SnailfishLeaf)

            self.replace_self(SnailfishLeaf(0))

            return ExplodeResult(True, self.left.value, self.right.value)

        if isinstance(self.left, SnailfishNumber):
            explode_result = self.left.explode(depth + 1)
            if explode_result.change_made:
                if explode_result.right_result:
                    leaf = self.right.find_left_leaf()
                    leaf.value += explode_result.right_result
                return ExplodeResult(True, explode_result.left_result, None)

        if isinstance(self.right, SnailfishNumber):
            explode_result = self.right.explode(depth + 1)
            if explode_result.change_made:
                if explode_result.left_result:
                    leaf = self.left.find_right_leaf()
                    leaf.value += explode_result.left_result
                return ExplodeResult(True, None, explode_result.right_result)
        return ExplodeResult(False)

    def split(self) -> bool:
        """Check for numbers above 9 and split them."""
        if self.left.split():
            return True
        return self.right.split()

    def reduce(self) -> None:
        """Reduce this Snailfish Number."""
        while True:
            explode_result = self.explode()
            if explode_result.change_made:
                continue
            if self.split():
                continue
            break

    @property
    def magnitude(self) -> int:
        """Compute the magnitude of the Snailfish Number."""
        return 3 * self.left.magnitude + 2 * self.right.magnitude


SnailfishNumberParser = pc.FunctionParser(pc.Line, SnailfishNumber.from_string)


@pc.parse(pc.Repeat(SnailfishNumberParser))
def run(nums: list[SnailfishNumber]) -> Result:
    """Solution for Day 18."""
    total = reduce(operator.add, nums)

    largest_magnitude = None
    for a, b in permutations(nums, 2):
        magnitude = (a + b).magnitude
        if largest_magnitude is None or magnitude > largest_magnitude:
            largest_magnitude = magnitude

    return Result(total.magnitude, largest_magnitude)
