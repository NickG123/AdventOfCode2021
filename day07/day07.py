"""Day 07."""

import math
import statistics
from typing import Callable

import utils.parser as pc
from result import Result


def fuel_cost(
    nums: list[int], target: int, fuel_cost_calc: Callable[[int], int]
) -> int:
    """Compute the total fuel to move each sub to a target position."""
    return sum(fuel_cost_calc(abs(x - target)) for x in nums)


def part2_movement_cost(distance: int) -> int:
    """Compute the fuel cost to move a sub distance in part 2."""
    return distance * (distance + 1) // 2


@pc.parse(pc.IntList)
def run(positions: list[int]) -> Result:
    """Solution for Day 07."""
    median = int(statistics.median(positions))
    mean = statistics.mean(positions)
    mean_low = int(math.floor(mean))
    mean_high = int(math.ceil(mean))

    part1 = fuel_cost(positions, median, lambda distance: distance)
    part2 = min(
        fuel_cost(positions, mean_low, part2_movement_cost),
        fuel_cost(positions, mean_high, part2_movement_cost),
    )

    return Result(part1, part2)
