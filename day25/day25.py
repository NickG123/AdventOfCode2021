"""Day 25."""


from enum import Enum
from itertools import count

import utils.parser as pc
from result import Result
from utils.geometry import Point2D, SizedGrid2D


class GridState(Enum):
    """Represents a spot on the grid."""

    EMPTY = "."
    RIGHT = ">"
    DOWN = "v"

    def __str__(self) -> str:
        """Convert to a string value."""
        return self.value


@pc.parse(pc.Lines)
def run(lines: list[str]) -> Result:
    """Solution for Day 25."""
    grid = SizedGrid2D.from_data([[GridState(c) for c in line] for line in lines])
    could_move = {
        GridState.RIGHT: {p for p, v in grid.items() if v == GridState.RIGHT},
        GridState.DOWN: {p for p, v in grid.items() if v == GridState.DOWN},
    }
    for turn_num in count(1):
        for dir, delta in [
            (GridState.RIGHT, Point2D(1, 0)),
            (GridState.DOWN, Point2D(0, 1)),
        ]:
            will_move = [
                p
                for p in could_move[dir]
                if grid[grid.get_pos_wrap(p + delta)] == GridState.EMPTY
            ]
            could_move[dir] = set()
            for p in will_move:
                dest = grid.get_pos_wrap(p + delta)
                grid[dest] = dir
                grid[p] = GridState.EMPTY
                could_move[dir].add(dest)

                for unblocked_dir, unblocked_delta in [
                    (GridState.RIGHT, Point2D(-1, 0)),
                    (GridState.DOWN, Point2D(0, -1)),
                ]:
                    unblocked = grid.get_pos_wrap(p + unblocked_delta)
                    if grid[unblocked] == unblocked_dir:
                        could_move[unblocked_dir].add(unblocked)

        if not could_move[GridState.DOWN] and not could_move[GridState.RIGHT]:
            break

    return Result(turn_num, None)
