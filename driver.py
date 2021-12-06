"""The driver program that is the main entrypoint for the application."""
import importlib
from datetime import datetime
from pathlib import Path

import click
from cookiecutter.main import cookiecutter

from driver_helpers.aoc_site import download_problem_input

YEAR = 2021
CURR_DAY = datetime.now().day


@click.group()
def cli() -> None:
    """Run the cli."""


@cli.command()
@click.argument("day", default=CURR_DAY)
def bootstrap(day: int) -> None:
    """Initialize a new folder for a day using the template and download the input."""
    day_str = str(day).zfill(2)
    cookiecutter("./template", extra_context={"day": day_str}, no_input=True)
    with (Path(f"day{day_str}") / "input").open("wb") as fout:
        download_problem_input(fout, YEAR, day)


@cli.command()
@click.argument("day", default=CURR_DAY)
@click.option("-i", "--input-file", "input_file_name", default="input")
def run(day: int, input_file_name: str) -> None:
    """Run the problem on the provided day."""
    day_str = str(day).zfill(2)
    input_file = Path(f"day{day_str}") / input_file_name
    if input_file_name == "input" and not input_file.is_file():
        with input_file.open("wb") as fout:
            download_problem_input(fout, YEAR, day_str)

    module = importlib.import_module(f"day{day_str}.day{day_str}")
    with open(input_file, "r", encoding="utf-8") as fin:
        result = module.run(fin)
    print(result)


if __name__ == "__main__":
    cli()
