"""Day 14."""

from collections import Counter
from functools import cache
from itertools import pairwise

import utils.parser as pc
from result import Result

Template = pc.IgnoreNewlines(pc.Word)
Rule = pc.Pair(pc.Word, pc.Word, separator=pc.Literal(" -> "))
Rules = pc.Dictionary(pc.Repeat(Rule, separator=pc.NewLine))


class PolymerBuilder:
    """A class that handles building polymers."""

    def __init__(self, rules: dict[str, str]) -> None:
        """Instantiate a new PolymerBuilder with the insertion rules."""
        self.rules = rules

    @cache
    def count_entries_after(self, polymer: str, steps: int) -> Counter[str]:
        """Count the number of elements in the polymer after a number of steps."""
        if steps == 0:
            return Counter(polymer)
        counts = Counter[str]()
        for e1, e2 in pairwise(polymer):
            new_entry = self.rules[e1 + e2]
            counts += self.count_entries_after(e1 + new_entry, steps - 1)
            counts += self.count_entries_after(new_entry + e2, steps - 1)
            # New entry is counted in both sides of the recursion
            counts[new_entry] -= 1
        # Every element except the first and last are counted in both sides of the pairwise
        counts -= Counter(polymer[1:-1])
        return counts


@pc.parse(pc.Pair(Template, Rules))
def run(data: tuple[str, dict[str, str]]) -> Result:
    """Solution for Day 14."""
    template, rules = data

    builder = PolymerBuilder(rules)
    part1 = builder.count_entries_after(template, 10)
    part2 = builder.count_entries_after(template, 40)

    return Result(
        max(part1.values()) - min(part1.values()),
        max(part2.values()) - min(part2.values()),
    )
