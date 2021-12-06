"""Day 03."""

from collections import Counter
from itertools import takewhile

import utils.parser as pc
from result import Result


def find_number(nums: list[str], most_common: bool, offset: int = 0) -> str:
    """Find the number matching the most/least common bits, starting from the left."""
    if len(nums) == 1:
        return nums[0]
    num_zeros = len(list(takewhile(lambda x: x == "0", (num[offset] for num in nums))))
    more_zeros = num_zeros > len(nums) // 2

    if more_zeros == most_common:
        sub_list = nums[:num_zeros]
    else:
        sub_list = nums[num_zeros:]

    return find_number(sub_list, most_common, offset + 1)


@pc.parse(pc.Lines)
def run(lines: list[str]) -> Result:
    """Solution for Day 03."""
    counts = [Counter([x]) for x in lines[0]]

    for row in lines[1:]:
        for counter, char in zip(counts, row):
            counter[char] += 1

    bit_mask = (1 << len(counts)) - 1
    gamma = int("".join(c.most_common()[0][0] for c in counts), 2)
    epsilon = gamma ^ bit_mask

    # Part 2 feels like sorting would be smarter
    sorted_nums = sorted(lines)
    oxygen = int(find_number(sorted_nums, True), 2)
    co2 = int(find_number(sorted_nums, False), 2)

    return Result(gamma * epsilon, oxygen * co2)
