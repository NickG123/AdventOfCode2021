"""Day 01."""

from itertools import islice, pairwise, tee

from file_parser import Parser
from result import Result


def run(parser: Parser) -> Result:
    """Solution for Day 01."""
    # Use pairwise to count the number of increases
    part1 = sum(b > a for a, b in pairwise(parser.read_ints()))

    # Basically do the same thing, except increase the end iterator by 3 instead of just 1
    window_start, window_end = tee(parser.read_ints())
    window_end = islice(window_end, 3, None)

    part2 = sum(
        num_adding > num_leaving
        for num_adding, num_leaving in zip(window_end, window_start)
    )

    return Result(part1, part2)
