"""Day 15."""
from __future__ import annotations

import heapq
from dataclasses import dataclass
from typing import Optional

import utils.parser as pc
from result import Result
from utils.geometry import Point2D, Rect2D, SizedGrid2D


@dataclass
class DijkstraNode:
    """A class to conain the risk and point, so that it can be put in a heapq."""

    total_risk: int
    point: Point2D

    def __lt__(self, other: DijkstraNode) -> bool:
        """Only compare the risk, ties don't matter."""
        return self.total_risk < other.total_risk


def dijkstra(risks: SizedGrid2D[int], destination: Point2D) -> int:
    """Run Dijkstra's algorithm over the grid to compute total risk."""
    total_risk: SizedGrid2D[Optional[int]] = SizedGrid2D.from_data(
        [[None] * risks.rect.width for _ in range(risks.rect.height)]
    )
    total_risk[risks.rect.top_left] = risks[risks.rect.top_left]

    to_visit = [DijkstraNode(0, risks.rect.top_left)]
    while to_visit:
        node = heapq.heappop(to_visit)
        if node.point == destination:
            return node.total_risk
        for neighbour_point, neighbour_risk in risks.neighbours(node.point):
            new_total_risk = node.total_risk + neighbour_risk
            neighbour_total_risk = total_risk[neighbour_point]
            if neighbour_total_risk is None or new_total_risk < neighbour_total_risk:
                total_risk[neighbour_point] = new_total_risk
                heapq.heappush(to_visit, DijkstraNode(new_total_risk, neighbour_point))

    raise Exception("Never reached target")


def build_part_2_risks(risks: SizedGrid2D[int], multiplier: int) -> SizedGrid2D[int]:
    """Build the part 2 grid."""
    new_grid = SizedGrid2D[int](
        Rect2D(Point2D(0, 0), risks.rect.bottom_right * multiplier)
    )

    for x_offset in range(multiplier):
        for y_offset in range(multiplier):
            for p, risk in risks.items():
                p = Point2D(
                    p.x + x_offset * risks.rect.width,
                    p.y + y_offset * risks.rect.height,
                )
                # It wraps to 1 instead of 0, so we need to add 1 for every time it wraps...
                quotient, remainder = divmod((risk + x_offset + y_offset), 10)
                new_grid[p] = remainder + quotient

    return new_grid


@pc.parse(pc.Repeat(pc.DigitList, separator=pc.NewLine))
def run(data: list[list[int]]) -> Result:
    """Solution for Day 15."""
    risks = SizedGrid2D.from_data(data)
    bottom_right_inclusive = risks.rect.bottom_right + Point2D(-1, -1)
    part2_risks = build_part_2_risks(risks, 5)
    part2_bottom_right_inclusive = part2_risks.rect.bottom_right + Point2D(-1, -1)

    part1 = dijkstra(risks, bottom_right_inclusive)
    part2 = dijkstra(part2_risks, part2_bottom_right_inclusive)

    return Result(part1, part2)
