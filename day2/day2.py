"""Day 2."""

from dataclasses import dataclass
from enum import Enum

from file_parser import Parser
from result import Result
from utils.geometry import Point2D


class Direction(Enum):
    """An enum capturing 2d direction based on name."""

    forward = Point2D(1, 0)
    down = Point2D(0, 1)
    up = Point2D(0, -1)


@dataclass
class Movement:
    """A class capturing a single movement instruction."""

    direction: Direction
    velocity: int

    @property
    def distance(self) -> Point2D:
        """Get the 2d distance travelled in this movement."""
        return self.direction.value * self.velocity


def run(parser: Parser) -> Result:
    """Solution for Day 2."""
    part1 = sum(
        (m.distance for m in parser.read_dataclass(Movement)),
        Point2D(0, 0),
    )

    part2 = Point2D(0, 0)
    aim = Point2D(0, 0)
    for movement in parser.read_dataclass(Movement):
        if movement.direction == Direction.forward:
            part2 += movement.distance
            part2 += aim * movement.velocity
        else:
            aim += movement.distance

    return Result(part1.x * part1.y, part2.x * part2.y)
