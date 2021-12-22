"""Day 22."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import prod
from typing import Iterator

import utils.parser as pc
from result import Result


class Action(Enum):
    """The reboot action."""

    on = True
    off = False


@dataclass(frozen=True)
class Cuboid:
    """Holds a 3d cuboid."""

    x_start: int
    x_end: int
    y_start: int
    y_end: int
    z_start: int
    z_end: int

    def bounds(self) -> Iterator[tuple[int, int]]:
        """Return an iterable of the bounds of each axis."""
        yield (self.x_start, self.x_end)
        yield (self.y_start, self.y_end)
        yield (self.z_start, self.z_end)

    @property
    def volume(self) -> int:
        """Return the area of this cuboid."""
        return prod(e - s + 1 for s, e in self.bounds())

    def overlaps(self, other: Cuboid) -> bool:
        """Check if this cuboid overlaps with another."""
        for (self_start, self_end), (other_start, other_end) in zip(
            self.bounds(), other.bounds()
        ):
            if other_end < self_start or other_start > self_end:
                return False
        return True

    def intersection(self, other: Cuboid) -> Cuboid:
        """Get the intersection of this cuboid with another."""
        assert self.overlaps(other)
        return Cuboid(
            max(self.x_start, other.x_start),
            min(self.x_end, other.x_end),
            max(self.y_start, other.y_start),
            min(self.y_end, other.y_end),
            max(self.z_start, other.z_start),
            min(self.z_end, other.z_end),
        )

    def remove(self, other: Cuboid) -> list[Cuboid]:
        """Remove another cuboid from this one, producing many new cuboids."""
        if not self.overlaps(other):
            return [self]
        other = self.intersection(other)
        # fmt: off
        result = [
            # Left and right fragments
            Cuboid(self.x_start, other.x_start - 1, self.y_start, self.y_end, self.z_start, self.z_end),
            Cuboid(other.x_end + 1, self.x_end, self.y_start, self.y_end, self.z_start, self.z_end),
            # Top and bottom fragments
            Cuboid(other.x_start, other.x_end, self.y_start, other.y_start - 1, self.z_start, self.z_end),
            Cuboid(other.x_start, other.x_end, other.y_end + 1, self.y_end, self.z_start, self.z_end),
            # Front and back fragments
            Cuboid(other.x_start, other.x_end, other.y_start, other.y_end, self.z_start, other.z_start - 1),
            Cuboid(other.x_start, other.x_end, other.y_start, other.y_end, other.z_end + 1, self.z_end),
        ]
        # fmt: on
        return [x for x in result if x.volume > 0]

    def __str__(self) -> str:
        """Create a string representation of the cuboid."""
        return f"{self.x_start}..{self.x_end},{self.y_start}..{self.y_end},{self.z_start}..{self.z_end}"


@dataclass
class RebootStep:
    """A class to hold a reboot step."""

    action: Action
    cuboid: Cuboid

    def __str__(self) -> str:
        """Create a string representation of the step."""
        return f"{self.action} {self.cuboid}"


IntRange = pc.Pair(pc.Int(), pc.Int(), separator=pc.Literal(".."))
Coordinate = pc.IgnorePrefix(pc.Pair(pc.Series(pc.Char(), pc.Literal("=")), IntRange))
Coordinates = pc.FunctionParser(
    pc.Repeat(Coordinate, separator=pc.Literal(",")),
    lambda x: Cuboid(*x[0], *x[1], *x[2]),
)
ActionParser = pc.Enumeration(Action)
RebootStepParser = pc.FunctionParser(
    pc.Pair(ActionParser, Coordinates, separator=pc.Literal(" ")),
    lambda x: RebootStep(*x),
)


@pc.parse(pc.Repeat(RebootStepParser, separator=pc.NewLine))
def run(steps: list[RebootStep]) -> Result:
    """Solution for Day 22."""
    part1_region = Cuboid(-50, 50, -50, 50, -50, 50)

    on_cubes: set[Cuboid] = set()
    for step in steps:
        for on_cube in set(on_cubes):
            on_cubes.remove(on_cube)
            for fragment in on_cube.remove(step.cuboid):
                on_cubes.add(fragment)
        if step.action == Action.on:
            on_cubes.add(step.cuboid)

    part1 = sum(
        part1_region.intersection(c).volume
        for c in on_cubes
        if part1_region.overlaps(c)
    )
    part2 = sum(c.volume for c in on_cubes)

    return Result(part1, part2)
