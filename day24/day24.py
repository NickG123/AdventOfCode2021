"""Day 24."""

from dataclasses import dataclass

import utils.parser as pc
from result import Result


@dataclass
class Constants:
    """A class to hold the constants of a single step."""

    z_div: int
    x_add: int
    y_add: int


def extract_constants(input: list[str]) -> list[Constants]:
    """Extract the constants for each step from the input."""
    result = []
    for offset in range(0, len(input), 18):
        z_div = int(input[offset + 4].split(" ")[-1])
        x_add = int(input[offset + 5].split(" ")[-1])
        y_add = int(input[offset + 15].split(" ")[-1])
        result.append(Constants(z_div, x_add, y_add))
    return result


@dataclass
class Constraint:
    """A class that holds the constraints on the input data."""

    input_digit: int
    modifier: int
    output_digit: int


# The code roughly decompiles to the following:
# (Where z_div is the constant on line 5, x_add on line 6 and y_add on line 16)
# def run_step(z: int, w: int, constants: Constants) -> int:
#     """Run a single verification step."""
#     x = not (((z % 26) + constants.x_add) == w)
#     return (z // constants.z_div) * (26 if x else 1) + (w + constants.y_add if x else 0)

# When x_add > 0, x_add is always > 9 and z_div is always 1
# Which means (((z % 26) + constants.x_add) == w) will never be true (since w < 10)
# Which means in that case it can be simplified further to:
# def run_step_positive_x_add(z: int, w: int, constants: Constants) -> int:
#     return (z * 26) + w + constants.y_add

# Looking at the above code, we can treat z as a stack of base-26 digits:

# When x_add > 0,
# z = (z * 26) + a will push on a
# When x_add < 0, z_div is always 26, so
# z = (z // 26) will pop
# Which will happen if w - constants.x_add is equal to the top number on our stack

# 7 of the 14 x_adds are positive, so we are "pushing" 7 numbers onto our stack
# We need to make it so that the other 7 calls are "popping" the same numbers off our stack
# Which will result in a 0
def get_constraints(constants: list[Constants]) -> list[Constraint]:
    """Compute all constraints on the input data."""
    constraints = []
    s = []
    for i, consts in enumerate(constants):
        if consts.x_add > 0:
            s.append((i, consts.y_add))
        else:
            push_index, y_add = s.pop()
            constraints.append(Constraint(push_index, y_add + consts.x_add, i))

    return constraints


@pc.parse(pc.Lines)
def run(lines: list[str]) -> Result:
    """Solution for Day 24."""
    constants = extract_constants(lines)
    constraints = get_constraints(constants)

    p1_digits = [0] * 14
    p2_digits = [0] * 14
    for constraint in constraints:
        # Because of the way we constructed it, we can always be sure input_digit < output_digit
        assert constraint.input_digit < constraint.output_digit
        high_digit = 9 - max(constraint.modifier, 0)
        p1_digits[constraint.output_digit] = high_digit + constraint.modifier
        p1_digits[constraint.input_digit] = high_digit
        low_digit = 1 - min(constraint.modifier, 0)
        p2_digits[constraint.output_digit] = low_digit + constraint.modifier
        p2_digits[constraint.input_digit] = low_digit

    return Result(
        "".join(str(d) for d in p1_digits),
        "".join(str(d) for d in p2_digits),
    )
