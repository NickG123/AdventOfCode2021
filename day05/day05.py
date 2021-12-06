"""Day 05."""
import utils.parser as pc
from result import Result
from utils.geometry import Grid2D, Point2D


@pc.parse(
    pc.Repeat(
        pc.Series(pc.Point2D, pc.Suppress(pc.Literal(" -> ")), pc.Point2D),
        separator=pc.NewLine,
    )
)
def run(points: list[tuple[Point2D, Point2D]]) -> Result:
    """Solution for Day 05."""
    p1_grid = Grid2D(default=int)
    p2_grid = Grid2D(default=int)
    for p1, p2 in points:
        for p in p1.points_between(p2):
            if p1.x == p2.x or p1.y == p2.y:
                p1_grid[p] += 1
            p2_grid[p] += 1

    return Result(
        sum(val > 1 for _, val in p1_grid.occupied_cells),
        sum(val > 1 for _, val in p2_grid.occupied_cells),
    )
