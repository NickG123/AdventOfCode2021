"""Day 02."""

from dataclasses import dataclass
from enum import Enum

import utils.parser as pc
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


MovementParser = pc.DataClass(
    Movement, pc.Series(pc.Enumeration(Direction), pc.Int(), separator=pc.Literal(" "))
)


@pc.parse(pc.Repeat(MovementParser, separator=pc.NewLine))
def run(moves: list[Movement]) -> Result:
    """Solution for Day 02."""
    part1 = sum(
        (m.distance for m in moves),
        Point2D(0, 0),
    )

    part2 = Point2D(0, 0)
    aim = Point2D(0, 0)
    for movement in moves:
        if movement.direction == Direction.forward:
            part2 += movement.distance
            part2 += aim * movement.velocity
        else:
            aim += movement.distance

    return Result(part1.x * part1.y, part2.x * part2.y)
