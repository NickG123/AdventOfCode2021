"""Day 08."""
from typing import Any

import utils.parser as pc
from result import Result
from utils.iterables import group_as_set

LENGTHS = {0: 6, 1: 2, 2: 5, 3: 5, 4: 4, 5: 5, 6: 6, 7: 3, 8: 7, 9: 6}
GROUPED_LENGTHS = group_as_set((v, k) for k, v in LENGTHS.items())
DETERMINISTIC_LENGTHS = {
    k: next(iter(v)) for k, v in GROUPED_LENGTHS.items() if len(v) == 1
}


SignalList = pc.Repeat(pc.FrozenSet(pc.Word), separator=pc.Literal(" "))
InputLine: pc.Parser[Any] = pc.Series(
    SignalList, pc.Suppress(pc.Literal(" | ")), SignalList
)


def pop_pattern(
    patterns: set[frozenset[str]], subset: frozenset[str] = None, invert: bool = False
) -> frozenset[str]:
    """Find a pattern that either does or doesn't contain a given subset and pop it from the set."""
    pattern = next(
        pattern
        for pattern in patterns
        if subset is None or (invert ^ (subset < pattern))
    )
    patterns.remove(pattern)
    return pattern


@pc.parse(pc.Repeat(InputLine, separator=pc.NewLine))
def run(lines: list[list[list[frozenset[str]]]]) -> Result:
    """Solution for Day 08."""
    part1 = 0
    part2 = 0
    for [input_patterns, output_patterns] in lines:
        part1 += sum(
            len(GROUPED_LENGTHS[len(output)]) == 1 for output in output_patterns
        )

        # First, fingerprint the patterns that we can easily identify
        fingerprints = {
            DETERMINISTIC_LENGTHS[len(pattern)]: pattern
            for pattern in input_patterns
            if len(pattern) in DETERMINISTIC_LENGTHS
        }

        # then, separate the patterns by length
        patterns_by_length = group_as_set((len(p), p) for p in input_patterns)

        # Next, fingerprint the patterns of length 5
        length_5_patterns = set(patterns_by_length[5])
        # We can identify 5 by checking if the fingerprint of 4 minus the fingerprint of 1 is a subset of the pattern
        fingerprints[5] = pop_pattern(
            length_5_patterns, fingerprints[4] - fingerprints[1]
        )
        # We can identify 3 by checking if the fingerprint of 1 is a subset of the pattern
        fingerprints[3] = pop_pattern(length_5_patterns, fingerprints[1])
        # 2 is whatever's left
        fingerprints[2] = pop_pattern(length_5_patterns)

        # Finally, fingerprint the patterns of length 6
        length_6_patterns = set(patterns_by_length[6])
        # We can identify 9 by checking if the fingerprint of 3 is a subset of the pattern
        fingerprints[9] = pop_pattern(length_6_patterns, fingerprints[3])
        # We can identify 6 by checking if the fingerprint of 1 is not a subset of the number
        fingerprints[6] = pop_pattern(length_6_patterns, fingerprints[1], invert=True)
        # 0 is whatever's left
        fingerprints[0] = pop_pattern(length_6_patterns)

        reverse_lookup = {
            pattern: fingerprint for fingerprint, pattern in fingerprints.items()
        }
        value = int(
            "".join(str(reverse_lookup[pattern]) for pattern in output_patterns)
        )
        part2 += value

    return Result(part1, part2)
