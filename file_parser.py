"""Parser for problem input files."""
from __future__ import annotations

import dataclasses
import re
from collections import Counter
from enum import Enum
from pathlib import Path
from typing import Callable, Iterator, Type, TypeVar

T = TypeVar("T")


def parse_field(s: str, typ: Type[T]) -> T:
    """Parse a string as the given type."""
    if typ in {int, str}:
        return typ(s)  # type: ignore
    if issubclass(typ, Enum):
        return typ[s]  # type: ignore
    raise Exception(f"Unkown type {typ}")


def parse_dataclass(data: list[str], clazz: Type[T]) -> T:
    """Parse a list of data into the provided dataclass."""
    assert len(data) == len(dataclasses.fields(clazz))
    parsed = [
        parse_field(d, field.type) for field, d in zip(dataclasses.fields(clazz), data)
    ]
    return clazz(*parsed)


class Parser:
    """A class that handles parsing input files."""

    def __init__(self, path: Path) -> None:
        """Create a new parser."""
        self.path = path

    def read_lines(self) -> Iterator[str]:
        """Read the lines of the file."""
        with self.path.open() as fin:
            for line in fin:
                yield line.strip()

    def read_chars(self) -> Iterator[str]:
        """Read the characters of a file (except newlines)."""
        for line in self.read_lines():
            for c in line:
                yield c

    def read_something(self, func: Callable[[str], T]) -> Iterator[T]:
        """Run a function on each line of the file."""
        return (func(line) for line in self.read_lines())

    def read_ints(self) -> Iterator[int]:
        """Read an int from each line of the file."""
        return self.read_something(int)

    def read_counts(self) -> Iterator[Counter[str]]:
        """Count the number of each character on each line in the file."""
        return self.read_something(Counter)

    def read_regex(self, regex: re.Pattern[str]) -> Iterator[re.Match[str]]:
        """Run a regex on each line and return the match.  Regex must match each line."""
        for match in self.read_something(regex.match):
            if match is None:
                raise ValueError("Regex did not match")
            yield match

    def read_regex_groups(self, regex: re.Pattern[str]) -> Iterator[dict[str, str]]:
        """Run a regex on each line and return the groups.  Regex must match each line."""
        return (regex.groupdict() for regex in self.read_regex(regex))

    def read_split(self, separator: str = " ") -> Iterator[list[str]]:
        """Split each line by a separator."""
        return self.read_something(lambda s: s.split(separator))

    def read_dataclass(self, clazz: Type[T], separator: str = " ") -> Iterator[T]:
        """Split the lines based on a separator and parse it into a dataclass."""
        return (parse_dataclass(d, clazz) for d in self.read_split(separator))

    def read_groups(self) -> Iterator[list[str]]:
        """Read lines a group at a time, separated by empty lines."""
        lines = []
        for line in self.read_lines():
            if line:
                lines.append(line)
            else:
                yield lines
                lines = []
        yield lines
