"""Day 05."""
import re

from file_parser import Parser
from result import Result
from utils.geometry import Grid2D, Point2D

LINE_REGEX = re.compile(r"(\d*),(\d*) -> (\d*),(\d*)")


def run(parser: Parser) -> Result:
    """Solution for Day 05."""
    points = (
        (Point2D(int(p1x), int(p1y)), Point2D(int(p2x), int(p2y)))
        for p1x, p1y, p2x, p2y in parser.read_regex_groups(LINE_REGEX)
    )

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
