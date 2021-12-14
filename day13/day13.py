"""Day 13."""

from dataclasses import dataclass
from enum import Enum

import utils.parser as pc
from result import Result
from utils.geometry import Grid2D, Point2D


def reflect(num: int, axis: int) -> int:
    """Reflect a number against an arbitrary axis if greater than the axis."""
    if num > axis:
        return 2 * axis - num
    return num


class FoldAxis(Enum):
    y = "y"
    x = "x"


@dataclass
class Fold:
    direction: FoldAxis
    offset: int

    def apply(self, point: Point2D) -> Point2D:
        """Apply the fold to a point."""
        return Point2D(
            reflect(point.x, self.offset) if self.direction == FoldAxis.x else point.x,
            reflect(point.y, self.offset) if self.direction == FoldAxis.y else point.y,
        )

    def run(self, grid: Grid2D[bool]) -> None:
        """Run fold on a grid."""
        for p, _ in list(grid.occupied_cells):
            new_p = self.apply(p)
            if new_p != p:
                grid[new_p] = True
                del grid[p]


FoldLine: pc.Parser[Fold] = pc.DataClass(
    Fold,
    pc.Series(
        pc.Suppress(pc.Literal("fold along ")),
        pc.Enumeration(FoldAxis),
        pc.Suppress(pc.Literal("=")),
        pc.Int(),
    ),
)
Folds = pc.Repeat(FoldLine, separator=pc.NewLine)
Moves = pc.IgnoreNewline(pc.Repeat(pc.Point2D, separator=pc.NewLine))


@pc.parse(pc.Pair(pc.IgnoreNewline(Moves), Folds))
def run(data: tuple[list[Point2D], list[Fold]]) -> Result:
    """Solution for Day 13."""
    points, folds = data
    grid = Grid2D[bool]()

    for p in points:
        grid[p] = True

    folds[0].run(grid)
    part1 = len(list(grid.occupied_cells))

    for fold in folds[1:]:
        fold.run(grid)

    part2 = grid.as_string(value_transformer=lambda s: "#", default=" ")

    return Result(part1, part2)
