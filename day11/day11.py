"""Day 11."""


from itertools import count

import utils.parser as pc
from result import Result
from utils.geometry import Point2D, SizedGrid2D


def increase_power(grid: SizedGrid2D[int], point: Point2D) -> bool:
    """Increase the power of a single octopus."""
    grid[point] += 1
    return grid[point] == 10


def step(grid: SizedGrid2D[int]) -> int:
    """Run a single step and count the flashes."""
    flashing: list[Point2D] = []
    for p, _ in grid.items():
        if increase_power(grid, p):
            flashing.append(p)

    for p in flashing:
        for neighbour, _ in grid.neighbours(p, diagonal=True):
            if increase_power(grid, neighbour):
                flashing.append(neighbour)

    for p in flashing:
        grid[p] = 0

    return len(flashing)


@pc.parse(pc.Repeat(pc.DigitList, separator=pc.NewLine))
def run(data: list[list[int]]) -> Result:
    """Solution for Day 11."""
    energy_levels = SizedGrid2D.from_data(data)
    total_jellyfish = len(data) * len(data[0])

    part1 = 0
    part2 = None

    for step_num in count(1):
        flashes = step(energy_levels)
        if step_num <= 100:
            part1 += flashes
        if flashes == total_jellyfish:
            part2 = step_num
        if part2 is not None and step_num > 100:
            break

    return Result(part1, part2)
