"""Day 06."""

from collections import Counter

import utils.parser as pc
from result import Result


def step(counts: Counter[int]) -> Counter[int]:
    """Advance time by one day."""
    new_counts = Counter({key - 1: value for key, value in counts.items() if key != 0})
    new_counts[6] += counts[0]
    new_counts[8] += counts[0]
    return new_counts


@pc.parse(pc.Counter(pc.IntList))
def run(counts: Counter[int]) -> Result:
    """Solution for Day 06."""
    for _ in range(80):
        counts = step(counts)

    part1 = sum(counts.values())

    for _ in range(176):
        counts = step(counts)

    part2 = sum(counts.values())

    print()

    return Result(part1, part2)
