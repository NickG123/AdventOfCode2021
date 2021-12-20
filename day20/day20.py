"""Day 20."""

from itertools import product

import utils.parser as pc
from result import Result
from utils.geometry import Grid2D, Point2D, SizedGrid2D


def compute_algo_offset(image: Grid2D[str], p: Point2D, infinite_char: str) -> int:
    """Compute the offset into the algorithm string to retrieve a pixel from."""
    result = 0
    for i, (dy, dx) in enumerate(product(range(-1, 2), repeat=2)):
        np = Point2D(p.x + dx, p.y + dy)
        char = image.get(np, infinite_char)
        result |= (char == "#") << (8 - i)
    return result


def run_step(image: Grid2D[str], algo: str, infinite_char: str) -> Grid2D[str]:
    """Run a single step of the enhancement algorithm."""
    bb = image.bounding_box()
    new_grid = Grid2D[str]()
    # Yep, I definitely labeled my corners wrong
    for y in range(bb.top_left.y - 1, bb.bottom_right.y + 1):
        for x in range(bb.top_left.x - 1, bb.bottom_right.x + 1):
            p = Point2D(x, y)
            offset = compute_algo_offset(image, p, infinite_char)
            new_val = algo[offset]
            new_grid[p] = new_val

    return new_grid


def run_steps(image: Grid2D[str], algo: str, num_steps: int) -> Grid2D[str]:
    """Run num_steps steps of the enhancement algorithm."""
    infinite_char = "."
    for _ in range(num_steps):
        image = run_step(image, algo, infinite_char)
        infinite_char = algo[-1] if infinite_char == "#" else algo[0]
    return image


@pc.parse(pc.Pair(pc.IgnoreNewline(pc.Line), pc.Lines))
def run(data: tuple[str, list[str]]) -> Result:
    """Solution for Day 20."""
    algo, image_data = data
    image = SizedGrid2D.from_data(image_data)

    result = run_steps(image, algo, 2)
    # Pretty slow, but manages to produce 50 iterations as is...
    result2 = run_steps(image, algo, 50)

    return Result(
        sum(val == "#" for _, val in result.occupied_cells),
        sum(val == "#" for _, val in result2.occupied_cells),
    )
