"""Helper utilities related to geometry."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterable, Optional, TypeVar


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


class Rect2D:
    """A class to capture a rectangle."""

    def __init__(self, top_left: Point2D, bottom_right: Point2D) -> None:
        """Construct a new rectangle from it's corner points."""
        if top_left.x > bottom_right.x or top_left.y > bottom_right.y:
            raise Exception("Invalid corner points for Rect2D")

        self.top_left = top_left
        self.bottom_right = bottom_right

    @property
    def width(self) -> int:
        """Get the width of the rectangle."""
        return self.bottom_right.x - self.top_left.x

    @property
    def height(self) -> int:
        """Get the height of the rectangle."""
        return self.bottom_right.y - self.top_left.y

    @property
    def col_nums(self) -> Iterable[int]:
        """Get the numbers of columns included in this rectangle."""
        return (i for i in range(self.top_left.x, self.bottom_right.x))

    @property
    def row_nums(self) -> Iterable[int]:
        """Get the numbers of rows included in this rectangle."""
        return (i for i in range(self.top_left.y, self.bottom_right.y))

    def contains_point(self, p: Point2D) -> bool:
        """Check if the rectangle contains a point."""
        return (
            self.top_left.x <= p.x < self.bottom_right.x
            and self.top_left.y <= p.y < self.bottom_right.y
        )


T = TypeVar("T")


class Grid2D(Generic[T]):
    """A class to capture a 2d grid."""

    def __init__(self, reverse_lookup: bool = False) -> None:
        """Initialize an empty grid."""
        self.data: dict[Point2D, T] = {}
        self.reverse_lookup = reverse_lookup
        self.reverse_lookup_dict: dict[T, Point2D] = {}

    def __setitem__(self, key: Point2D, val: T) -> None:
        """Set a position in the grid."""
        if self.reverse_lookup is not None:
            self.reverse_lookup_dict[val] = key
        self.data[key] = val

    def __getitem__(self, key: Point2D) -> T:
        """Get a value at a posiition on the grid."""
        return self.data[key]

    def find(self, val: T) -> Optional[Point2D]:
        """Reverse lookup the position of a value."""
        if not self.reverse_lookup:
            raise Exception("Tried to find value with reverse lookup disabled.")
        return self.reverse_lookup_dict.get(val)


class SizedGrid2D(Grid2D[T]):
    """A class to capture a 2d grid with a specific size."""

    def __init__(self, rect: Rect2D, reverse_lookup: bool = False) -> None:
        """Initialize an empty sized grid."""
        self.rect = rect
        super().__init__(reverse_lookup=reverse_lookup)

    def __setitem__(self, key: Point2D, val: T) -> None:
        """Set a position in the grid."""
        if not self.rect.contains_point(key):
            raise Exception(f"Point {key} out of bounds")
        super().__setitem__(key, val)

    def __getitem__(self, key: Point2D) -> T:
        """Get a value at a posiition on the grid."""
        if not self.rect.contains_point(key):
            raise Exception(f"Point {key} out of bounds")
        return super().__getitem__(key)

    @staticmethod
    def from_data(data: list[list[T]], reverse_lookup: bool = False) -> SizedGrid2D[T]:
        """Construct a sized grid from a 2d array."""
        height = len(data)
        width = len(data[0])
        grid = SizedGrid2D[T](
            Rect2D(Point2D(0, 0), Point2D(width, height)), reverse_lookup=reverse_lookup
        )
        for y, row in enumerate(data):
            for x, cell in enumerate(row):
                grid[Point2D(x, y)] = cell
        return grid

    def row(self, row_num: int) -> Iterable[T]:
        """Get a row of the grid."""
        return (self[Point2D(col_num, row_num)] for col_num in self.rect.col_nums)

    def col(self, col_num: int) -> Iterable[T]:
        """Get a column of the grid."""
        return (self[Point2D(col_num, row_num)] for row_num in self.rect.row_nums)

    @property
    def rows(self) -> Iterable[Iterable[T]]:
        """Get the rows of the grid."""
        for row_num in self.rect.row_nums:
            yield self.row(row_num)

    @property
    def cols(self) -> Iterable[Iterable[T]]:
        """Get the rows of the grid."""
        for col_num in self.rect.col_nums:
            yield self.col(col_num)

    @property
    def cells(self) -> Iterable[T]:
        """Get the cells of the grid."""
        for row in self.rows:
            for cell in row:
                yield cell

    def __str__(self) -> str:
        """Simple string representation of the grid."""
        return "\n".join(" ".join(str(s) for s in row) for row in self.rows)
