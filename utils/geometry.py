"""Helper utilities related to geometry."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Generic, Iterable, Optional, Sequence, TypeVar


def get_basis_vector(x: int) -> int:
    """Get a basis vector from an int."""
    if x == 0:
        return 0
    return -1 if x < 0 else 1


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

    def points_between(self, other: Point2D) -> Iterable[Point2D]:
        """Get the points between this point and another point."""
        y_vector = other.y - self.y
        x_vector = other.x - self.x

        if x_vector != 0 and y_vector != 0 and abs(x_vector) != abs(y_vector):
            raise Exception(
                "Tried to get points between two points that are not aligned."
            )

        return self.points_in_path(
            Point2D(get_basis_vector(x_vector), get_basis_vector(y_vector)),
            max(abs(x_vector), abs(y_vector)),
        )

    def points_in_path(
        self, direction: Point2D, max_distance: int
    ) -> Iterable[Point2D]:
        """Get the points in a path starting with this point and heading in one direction for a distance."""
        for distance in range(max_distance + 1):
            yield self + direction * distance


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


CARDINAL_DIRECTIONS = [Point2D(-1, 0), Point2D(1, 0), Point2D(0, -1), Point2D(0, 1)]
ALL_DIRECTIONS = CARDINAL_DIRECTIONS + [
    Point2D(-1, -1),
    Point2D(1, 1),
    Point2D(1, -1),
    Point2D(-1, 1),
]
T = TypeVar("T")


class Grid2D(Generic[T]):
    """A class to capture a 2d grid."""

    def __init__(
        self, reverse_lookup: bool = False, default: Optional[Callable[[], T]] = None
    ) -> None:
        """Initialize an empty grid."""
        self.data: dict[Point2D, T] = {} if default is None else defaultdict(default)
        self.reverse_lookup = reverse_lookup
        self.reverse_lookup_dict: dict[T, Point2D] = {}

    def __setitem__(self, key: Point2D, val: T) -> None:
        """Set a position in the grid."""
        if self.reverse_lookup:
            self.reverse_lookup_dict[val] = key
        self.data[key] = val

    def __getitem__(self, key: Point2D) -> T:
        """Get a value at a posiition on the grid."""
        return self.data[key]

    def __delitem__(self, key: Point2D) -> None:
        """Delete a value at a position on the grid."""
        del self.data[key]

    def get(self, key: Point2D, default: T) -> T:
        """Get a value or return a default.  I should really just inherit from MutableMapping..."""
        return self.data.get(key, default)

    def find(self, val: T) -> Optional[Point2D]:
        """Reverse lookup the position of a value."""
        if not self.reverse_lookup:
            raise Exception("Tried to find value with reverse lookup disabled.")
        return self.reverse_lookup_dict.get(val)

    def neighbours(
        self, key: Point2D, diagonal: bool = False
    ) -> Iterable[tuple[Point2D, T]]:
        """Return the neighbours of a given point, if defined."""
        directions = ALL_DIRECTIONS if diagonal else CARDINAL_DIRECTIONS
        return (
            (key + offset, self.data[key + offset])
            for offset in directions
            if key + offset in self.data
        )

    def bounding_box(self) -> Rect2D:
        """Get the rectangle containing all points in the dataset"""
        min_x = min(p.x for p in self.data)
        max_x = max(p.x for p in self.data)
        min_y = min(p.y for p in self.data)
        max_y = max(p.y for p in self.data)
        return Rect2D(Point2D(min_x, min_y), Point2D(max_x + 1, max_y + 1))

    @property
    def occupied_cells(self) -> Iterable[tuple[Point2D, T]]:
        """Get any cells that have been filled in."""
        return self.data.items()

    def as_string(self, *, value_transformer: Callable[[T], str], default: str) -> str:
        """Convert the grid to a string."""
        bb = self.bounding_box()
        result_fragments = []
        for row_num in bb.row_nums:
            for col_num in bb.col_nums:
                p = Point2D(col_num, row_num)
                if p in self.data:
                    result_fragments.append(value_transformer(self.data[p]))
                else:
                    result_fragments.append(default)
            result_fragments.append("\n")
        return "".join(result_fragments)


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
    def from_data(
        data: Sequence[Sequence[T]], reverse_lookup: bool = False
    ) -> SizedGrid2D[T]:
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

    def items(self) -> Iterable[tuple[Point2D, T]]:
        """Get the points and cells of the grid."""
        for row_num in self.rect.row_nums:
            for col_num in self.rect.col_nums:
                point = Point2D(col_num, row_num)
                yield point, self.data[point]

    def get_pos_wrap(self, p: Point2D) -> Point2D:
        """Get a position from the grid, wrapping around if out of bounds."""
        x = ((p.x - self.rect.top_left.x) % self.rect.width) + self.rect.top_left.x
        y = ((p.y - self.rect.top_left.y) % self.rect.height) + self.rect.top_left.y
        return Point2D(x, y)

    def __str__(self) -> str:
        """Simple string representation of the grid."""
        return "\n".join(" ".join(str(s) for s in row) for row in self.rows)
