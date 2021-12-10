"""Day 10."""

import statistics
from functools import reduce

import utils.parser as pc
from result import Result

PAIRS = {"(": ")", "[": "]", "{": "}", "<": ">"}
P1_POINTS = {")": 3, "]": 57, "}": 1197, ">": 25137}
P2_POINTS = {"(": 1, "[": 2, "{": 3, "<": 4}


@pc.parse(pc.Lines)
def run(lines: list[str]) -> Result:
    """Solution for Day 10."""
    part1 = 0
    p2_scores = []
    for line in lines:
        bracket_stack = []
        for c in line:
            if c in PAIRS:
                bracket_stack.append(c)
            else:
                opener = bracket_stack.pop()
                if c != PAIRS[opener]:
                    part1 += P1_POINTS[c]
                    break
        else:
            p2_scores.append(
                reduce(lambda a, b: 5 * a + P2_POINTS[b], reversed(bracket_stack), 0)
            )

    return Result(part1, statistics.median_low(p2_scores))
