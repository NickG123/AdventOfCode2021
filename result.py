"""Problem result dataclass."""
from dataclasses import dataclass
from typing import Any


@dataclass
class Result:
    """A class to hold the result of a problem."""

    part1: Any
    part2: Any

    def __str__(self) -> str:
        return f"Part 1 Result:\n{self.part1}\nPart 2 Result:\n{self.part2}"
