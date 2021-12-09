"""Day 09."""

import heapq
import operator
from collections import deque
from functools import reduce

import utils.parser as pc
from result import Result
from utils.geometry import Point2D, SizedGrid2D


def find_basin_size(grid: SizedGrid2D[int], start_point: Point2D) -> int:
    """Find the size of a basin starting at a point within the basin."""
    visited = set()
    to_visit = deque([start_point])

    while len(to_visit) > 0:
        node = to_visit.popleft()
        visited.add(node)

        for neighbour, neighbour_value in grid.neighbours(node):
            if neighbour not in visited and neighbour_value != 9:
                to_visit.append(neighbour)

    return len(visited)


@pc.parse(pc.Repeat(pc.DigitList, separator=pc.NewLine))
def run(data: list[list[int]]) -> Result:
    """Solution for Day 09."""
    grid = SizedGrid2D.from_data(data)

    part1 = 0
    basin_sizes = []
    for point, cell in grid.items():
        if cell < min(c for p, c in grid.neighbours(point)):
            part1 += 1 + cell
            basin_sizes.append(find_basin_size(grid, point))

    part2 = reduce(operator.mul, heapq.nlargest(3, basin_sizes))
    return Result(part1, part2)
