"""Day 17."""


from typing import Optional

import utils.parser as pc
from result import Result
from utils.geometry import Point2D, Rect2D

AxisCoords = pc.Pair(pc.Int(), pc.Int(), separator=pc.Literal(".."))
TargetArea = pc.Pair(
    pc.IgnorePrefix(pc.Pair(pc.Literal("x="), AxisCoords)),
    pc.IgnorePrefix(pc.Pair(pc.Literal("y="), AxisCoords)),
    separator=pc.Literal(", "),
)
InputParser = pc.FunctionParser(
    pc.IgnorePrefix(pc.Pair(pc.Literal("target area: "), TargetArea)),
    lambda x: Rect2D(Point2D(x[0][0], x[1][0]), Point2D(x[0][1] + 1, x[1][1] + 1)),
)


def send_probe(velocity: Point2D, target: Rect2D) -> Optional[int]:
    """Send a probe out from 0, 0, return max height reached if it hits target."""
    current_position = Point2D(0, 0)
    max_height = None
    while (
        current_position.x < target.bottom_right.x
        and current_position.y > target.top_left.y
    ):
        current_position += velocity

        if max_height is None or current_position.y > max_height:
            max_height = current_position.y

        if velocity.x != 0:
            velocity += Point2D(-1, 0)
        velocity += Point2D(0, -1)

        if target.contains_point(current_position):
            return max_height
    return None


@pc.parse(InputParser)
def run(target: Rect2D) -> Result:
    """Solution for Day 17."""
    max_x_vel = target.bottom_right.x + 1
    min_y_vel = target.top_left.y
    max_y_vel = abs(target.top_left.y)

    part1 = None
    part2 = 0

    for x_vel in range(max_x_vel):
        for y_vel in range(min_y_vel, max_y_vel):
            height_reached = send_probe(Point2D(x_vel, y_vel), target)
            if height_reached is not None:
                part2 += 1
                if part1 is None or height_reached > part1:
                    part1 = height_reached

    return Result(part1, part2)
