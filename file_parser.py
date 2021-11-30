"""Parser for problem input files."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Callable, Iterator, TypeVar

T = TypeVar("T")


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
