"""Day 03."""

from collections import Counter
from itertools import takewhile

from file_parser import Parser
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


def run(parser: Parser) -> Result:
    """Solution for Day 03."""
    it = parser.read_lines()
    counts = [Counter([x]) for x in next(it)]

    for row in it:
        for counter, char in zip(counts, row):
            counter[char] += 1

    bit_mask = (1 << len(counts)) - 1
    gamma = int("".join(c.most_common()[0][0] for c in counts), 2)
    epsilon = gamma ^ bit_mask

    # Part 2 feels like sorting would be smarter
    sorted_nums = sorted(parser.read_lines())
    oxygen = int(find_number(sorted_nums, True), 2)
    co2 = int(find_number(sorted_nums, False), 2)

    return Result(gamma * epsilon, oxygen * co2)
