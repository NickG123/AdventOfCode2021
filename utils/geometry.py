"""Helper utilities related to geometry."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Point2D:
    """A class to capture a 2d point."""

    x: int
    y: int

    def __add__(self, other: Point2D) -> Point2D:
        """Add another point to this one."""
        return Point2D(self.x + other.x, self.y + other.y)

    def __iadd__(self, other: Point2D) -> Point2D:
        """Add another point to this one."""
        return self + other

    def __mul__(self, scalar: int) -> Point2D:
        """Multiplay this point by a scalar."""
        return Point2D(self.x * scalar, self.y * scalar)
