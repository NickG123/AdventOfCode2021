"""Day 23."""
from __future__ import annotations

from copy import deepcopy
from enum import Enum
from typing import Optional

import utils.parser as pc
from result import Result
from utils.geometry import Grid2D, Point2D

MOVE_COST = {"A": 1, "B": 10, "C": 100, "D": 1000}


class GridStatus(Enum):
    """Options for cells that do not contain amphipods."""

    WALL = "#"
    EMPTY = "."
    INTERSECTION = "x"


class Amphipod:
    """Represents an amphipod."""

    def __init__(self, label: str, first_side_room: int, position: Point2D) -> None:
        """Create a new amphipod."""
        self.label = label
        self.dest_x = first_side_room + 2 * (ord(label) - ord("A"))
        self.position = position
        self.done = False

    def move(self, position: Point2D) -> Amphipod:
        """Move the amphipod and check if it's done."""
        result = deepcopy(self)
        result.position = position
        if result.position.x == result.dest_x:
            result.done = True
        return result

    def move_cost(self, steps: int) -> int:
        """Get the cost of moving this amphipod a number of steps."""
        return steps * MOVE_COST[self.label]

    def __str__(self) -> str:
        """Get a string representation of the amphipod."""
        return self.label


class Burrow:
    """Represents the burrow."""

    def __init__(self, rows: list[str]) -> None:
        """Construct a new burrow."""
        self.grid = Grid2D[GridStatus]()
        first_side_room = None
        side_room_y = None
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                p = Point2D(x, y)
                if c == " ":
                    continue
                if c in MOVE_COST:
                    if first_side_room is None:
                        first_side_room = x
                    if side_room_y is None:
                        side_room_y = y
                    if y == side_room_y:
                        self.grid[Point2D(x, y - 1)] = GridStatus.INTERSECTION
                    self.grid[p] = GridStatus.EMPTY
                else:
                    self.grid[p] = GridStatus(c)

        assert side_room_y is not None
        assert first_side_room is not None
        self.side_room_y = side_room_y
        self.side_room_y_end = side_room_y + 1
        self.first_side_room = first_side_room
        self.hall_points = [
            Point2D(x, self.side_room_y - 1)
            for x in range(0, self.grid.bounding_box().width)
            if self.grid[Point2D(x, self.side_room_y - 1)] == GridStatus.EMPTY
        ]

        self.paths = self.compute_paths()

    def compute_paths(self) -> dict[tuple[Point2D, Point2D], frozenset[Point2D]]:
        """Pre-compute all paths in the grid."""
        paths = {}
        for p1, status in self.grid.occupied_cells:
            if status == GridStatus.EMPTY:
                visited = {p1}
                to_visit = [[p] for p, _ in self.grid.neighbours(p1)]
                for path in to_visit:
                    node = path[-1]
                    visited.add(node)
                    if self.grid[node] == GridStatus.EMPTY:
                        paths[(p1, node)] = frozenset(path)
                    if self.grid[node] in {GridStatus.EMPTY, GridStatus.INTERSECTION}:
                        to_visit.extend(
                            path + [p]
                            for p, _ in self.grid.neighbours(node)
                            if p not in visited
                        )
        return paths

    def amphipod_moves(
        self, amphipod: Amphipod, others: dict[Point2D, Amphipod]
    ) -> list[tuple[Point2D, int]]:
        """Get a list of moves the provided amphipod could take."""
        if amphipod.done:
            return []

        # If the amphipod is not in a side room, only move is to go into it's side room
        if amphipod.position.y < self.side_room_y:
            for y in range(self.side_room_y_end, self.side_room_y - 1, -1):
                dest = Point2D(amphipod.dest_x, y)
                path = self.paths[(amphipod.position, dest)]
                if not path.intersection(others):
                    return [(dest, len(path))]
                existing = others.get(dest)
                if existing is None or existing.label != amphipod.label:
                    return []
        results = []
        for p in self.hall_points:
            path = self.paths[(amphipod.position, p)]
            if not path.intersection(others):
                results.append((p, len(path)))
        return results

    def __str__(self) -> str:
        """Return a string representation of this burrow."""
        return self.grid.as_string(
            value_transformer=lambda x: x.value
            if isinstance(x, GridStatus)
            else str(x),
            default="#",
        )


def find_solution(
    burrow: Burrow,
    amphipods: dict[Point2D, Amphipod],
    memo: Optional[dict[frozenset[tuple[str, Point2D]], Optional[int]]] = None,
) -> int | None:
    """Run all possible movements of Amphipods and return the lowest cost."""
    if memo is None:
        memo = {}

    memo_key = frozenset(
        (amphipod.label, amphipod.position) for amphipod in amphipods.values()
    )
    if memo_key in memo:
        return memo[memo_key]

    lowest_cost = None
    moves = [
        (amphipod, move, steps)
        for amphipod in amphipods.values()
        for move, steps in burrow.amphipod_moves(amphipod, amphipods)
    ]
    if len(moves) == 0:
        if all(a.done for a in amphipods.values()):
            return 0
        else:
            return None

    for amphipod, move, steps in moves:
        new_amphipod = amphipod.move(move)
        new_amphipods = {k: v for k, v in amphipods.items() if v != amphipod}
        new_amphipods[move] = new_amphipod
        sub_cost = find_solution(burrow, new_amphipods, memo)
        if sub_cost is not None:
            total_cost = sub_cost + amphipod.move_cost(steps)
            if lowest_cost is None or total_cost < lowest_cost:
                lowest_cost = total_cost

    memo[memo_key] = lowest_cost
    return lowest_cost


@pc.parse(pc.Lines)
def run(lines: list[str]) -> Result:
    """Solution for Day 23."""
    burrow = Burrow(lines)
    part2_burrow = deepcopy(burrow)
    amphipods = {}
    for y, row in enumerate(lines):
        for x, cell in enumerate(row):
            if cell in MOVE_COST:
                p = Point2D(x, y)
                amphipods[p] = Amphipod(cell, burrow.first_side_room, p)
    part2_amphipods = deepcopy(amphipods)
    part1 = find_solution(burrow, amphipods)

    for y in range(0, 4):
        for x in range(
            part2_burrow.first_side_room, part2_burrow.first_side_room + 8, 2
        ):
            part2_burrow.grid[
                Point2D(x, y + part2_burrow.side_room_y)
            ] = GridStatus.EMPTY
            part2_burrow.grid[
                Point2D(x, y + part2_burrow.side_room_y + 1)
            ] = GridStatus.WALL

    # It's horrendous, but we're just gonna manually build part 2
    for amphipod in list(part2_amphipods.values()):
        if amphipod.position.y > part2_burrow.side_room_y:
            new_position = Point2D(amphipod.position.x, amphipod.position.y + 2)
            amphipod = amphipod.move(new_position)
            part2_amphipods[new_position] = amphipod

    for p, label in [
        (Point2D(3, 3), "D"),
        (Point2D(5, 3), "C"),
        (Point2D(7, 3), "B"),
        (Point2D(9, 3), "A"),
        (Point2D(3, 4), "D"),
        (Point2D(5, 4), "B"),
        (Point2D(7, 4), "A"),
        (Point2D(9, 4), "C"),
    ]:
        part2_amphipods[p] = Amphipod(label, part2_burrow.first_side_room, p)
    part2_burrow.paths = part2_burrow.compute_paths()
    part2_burrow.side_room_y_end += 2

    part2 = find_solution(part2_burrow, part2_amphipods)

    return Result(part1, part2)
