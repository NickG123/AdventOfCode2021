"""Day 19."""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations, permutations
from typing import Callable, Iterable, Iterator

import utils.parser as pc
from result import Result


@dataclass(frozen=True)
class Point3D:
    """A class to hold a 3d point."""

    x: int
    y: int
    z: int

    def __iter__(self) -> Iterator[int]:
        """Allow iteration over each coordinate."""
        yield self.x
        yield self.y
        yield self.z

    def dot(self, other: Point3D) -> int:
        """Apply the dot product of two matrices."""
        return sum(a * b for a, b in zip(self, other))

    def apply_matrix(self, mat: tuple[Point3D, Point3D, Point3D]) -> Point3D:
        """Return a new point by applying a matrix to this point."""
        return Point3D(*[self.dot(row) for row in mat])

    def distance(self, other: Point3D) -> Point3D:
        """Return the distance vector between two points."""
        return Point3D(
            abs(self.x - other.x), abs(self.y - other.y), abs(self.z - other.z)
        )

    def manhatten_distance(self, other: Point3D) -> int:
        """Compute manhatten distance between two points."""
        return sum(self.distance(other))

    def __sub__(self, other: Point3D) -> Point3D:
        """Return a vector containing the diference between two points."""
        # Probably should actually create a vector class for safety, but ¯\_(ツ)_/¯
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __add__(self, other: Point3D) -> Point3D:
        """Add a vector to a point."""
        return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __str__(self) -> str:
        """Generate a string representation."""
        return f"{self.x},{self.y},{self.z}"


def int_cos_sin(func: Callable[[float], float], degrees: int) -> int:
    """Perform sine or cosine on integers."""
    assert degrees in {0, 90, 180, 270}
    return int(round(func(math.radians(degrees))))


def generate_rotation_matrix(
    x_rot: int, y_rot: int, z_rot: int
) -> tuple[Point3D, Point3D, Point3D]:
    """Generate an int rotation matrix."""
    cos_x_rot = int_cos_sin(math.cos, x_rot)
    sin_x_rot = int_cos_sin(math.sin, x_rot)
    cos_y_rot = int_cos_sin(math.cos, y_rot)
    sin_y_rot = int_cos_sin(math.sin, y_rot)
    cos_z_rot = int_cos_sin(math.cos, z_rot)
    sin_z_rot = int_cos_sin(math.sin, z_rot)

    # Stolen shamelessly from https://en.wikipedia.org/wiki/Rotation_matrix#General_rotations
    return (
        Point3D(
            cos_z_rot * cos_y_rot,
            cos_z_rot * sin_y_rot * sin_x_rot - sin_z_rot * cos_x_rot,
            cos_z_rot * sin_y_rot * cos_x_rot + sin_z_rot * sin_x_rot,
        ),
        Point3D(
            sin_z_rot * cos_y_rot,
            sin_z_rot * sin_y_rot * sin_x_rot + cos_z_rot * cos_x_rot,
            sin_z_rot * sin_y_rot * cos_x_rot - cos_z_rot * sin_x_rot,
        ),
        Point3D(-sin_y_rot, cos_y_rot * sin_x_rot, cos_y_rot * cos_x_rot),
    )


def compute_distances(positions: Iterable[Point3D]) -> set[Point3D]:
    """Compute every distance between every pair of points."""
    return {p1.distance(p2) for p1, p2 in permutations(positions, 2)}


class Rotation:
    """A class that holds a single rotation of points."""

    def __init__(
        self, matrix: tuple[Point3D, Point3D, Point3D], positions: list[Point3D]
    ) -> None:
        """Construct a new rotation and pre-compute the distances between the points."""
        self.matrix = matrix
        self.positions = positions
        self.distances = compute_distances(positions)


class Scanner:
    """A clas containing a scanner and it's relatively scanned beacons."""

    def __init__(self, positions: list[Point3D]) -> None:
        """Construct a new scanner from it's beacon positions."""
        self.positions = positions
        self.rotations = self.generate_rotations()

    def generate_rotations(self) -> list[Rotation]:
        """Get all rotations of this scanner."""
        matrices = []
        # Generate all rotations where z rotation is 0
        for x_rotation in [0, 90, 180, 270]:
            for y_rotation in [0, 90, 180, 270]:
                matrices.append(generate_rotation_matrix(x_rotation, y_rotation, 0))

        # Generate the remaining rotations
        for x_rotation in [0, 90, 180, 270]:
            for z_rotation in [90, 270]:
                matrices.append(generate_rotation_matrix(x_rotation, 0, z_rotation))

        result = []
        for matrix in matrices:
            new_points = []
            for p in self.positions:
                new_points.append(p.apply_matrix(matrix))
            result.append(Rotation(matrix, new_points))
        return result


def find_matching_rotation(
    world_positions: set[Point3D], world_distances: set[Point3D], scanner: Scanner
) -> tuple[set[Point3D], Point3D] | None:
    """Find the rotation that matches 12 points in the world positions if possible."""
    for rotation in scanner.rotations:
        # If the rotation and the world share 12 points in common that have been shifted
        # The list of all distances between poitns should share at least 12 * 11 / 2 or 66 distance
        # In some edge case it might be possible that this happens by accident?
        # So we'll check for 12 common points later.
        # This just prevents us from having to do an n^3 operation on every pair of scanners.
        if len(world_distances & rotation.distances) >= 66:
            for world_p in world_positions:
                for p in rotation.positions:
                    shift = world_p - p
                    shifted = {x + shift for x in rotation.positions}
                    common_points = world_positions & shifted
                    if len(common_points) >= 12:
                        return shifted, shift
    return None


Header = pc.IgnoreNewline(
    pc.Series(pc.Literal("--- scanner "), pc.Int(), pc.Literal(" ---"))
)
Positions = pc.FunctionParser(
    pc.Repeat(pc.Int(), separator=pc.Literal(","), min=1), lambda x: Point3D(*x)
)
ScannerParser = pc.IgnoreNewline(
    pc.IgnorePrefix(
        pc.Pair(
            Header,
            pc.FunctionParser(pc.Repeat(Positions, separator=pc.NewLine), Scanner),
        )
    )
)


@pc.parse(pc.Repeat(ScannerParser, separator=pc.NewLine))
def run(scanners: list[Scanner]) -> Result:
    """Solution for Day 19."""
    first_scanner = scanners[0]
    world = set(first_scanner.rotations[0].positions)
    scanners_to_check = [world]

    scanners_left = set(scanners[1:])
    scanner_positions = [Point3D(0, 0, 0)]

    for world_scanner in scanners_to_check:
        world_distances = compute_distances(world_scanner)
        for scanner in set(scanners_left):
            result = find_matching_rotation(world_scanner, world_distances, scanner)
            if result:
                new_world_points, scanner_position = result
                scanner_positions.append(scanner_position)
                world.update(new_world_points)
                scanners_to_check.append(new_world_points)
                scanners_left.remove(scanner)

    assert len(scanners_left) == 0

    return Result(
        len(world),
        max(a.manhatten_distance(b) for a, b in combinations(scanner_positions, 2)),
    )
