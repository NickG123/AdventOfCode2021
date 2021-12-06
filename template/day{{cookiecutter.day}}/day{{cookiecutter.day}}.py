"""Day {{cookiecutter.day}}."""

import utils.parser as pc
from result import Result


@pc.parse(pc.Lines)
def run(lines: list[str]) -> Result:
    """Solution for Day {{cookiecutter.day}}."""
    return Result(None, None)
