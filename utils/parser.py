"""A simple parser combinator utility."""
import string
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Generic, Optional, TextIO, Type, TypeVar

from result import Result as ProblemResult

from utils.geometry import Point2D as Point2DObj

T = TypeVar("T")
S = TypeVar("S")


@dataclass
class ParseResult(Generic[T]):
    """A class to hold the result of a parse."""

    result: T
    new_offset: int


class ParseException(Exception):
    """Exception raised when there is a parsing error."""


class Parser(Generic[T], metaclass=ABCMeta):
    """Base class for all parsers."""

    def parse_file(self, file: Path | str | TextIO) -> T:
        """Parse a file, by path or filelike."""
        if isinstance(file, (str, Path)):
            with open(file, "r", encoding="utf-8") as fin:
                return self.parse_string(fin.read())
        return self.parse_string(file.read())

    def parse_string(self, data: str) -> T:
        """Parse a string."""
        return self._parse(data, 0).result

    def _parse(self, data: str, offset: int) -> ParseResult[T]:
        """Run the parse."""
        return self._parse_impl(data, offset)

    @abstractmethod
    def _parse_impl(self, data: str, offset: int) -> ParseResult[T]:
        """Run the actual parse implementation."""


class Char(Parser[str]):
    """Parses a single character."""

    def __init__(
        self, allowed_chars: Optional[str] = None, illegal_chars: str = "\n"
    ) -> None:
        """Construct a Character parser."""
        self.allowed_chars = set(allowed_chars) if allowed_chars is not None else None
        self.illegal_chars = set(illegal_chars)

    def _parse_impl(self, data: str, offset: int) -> ParseResult[str]:
        if offset == len(data):
            raise ParseException(
                f"Expected {f'one of {self.allowed_chars}' if self.allowed_chars is not None else 'a character'} but reached end of input"
            )
        if self.allowed_chars is not None and data[offset] not in self.allowed_chars:
            raise ParseException(
                f"Expected one of {self.allowed_chars} but found {data[offset]}"
            )
        if data[offset] in self.illegal_chars:
            raise ParseException(
                f"Expected no {self.illegal_chars} but found {data[offset]}"
            )
        return ParseResult(data[offset], offset + 1)


class Repeat(Parser[list[T]]):
    """Runs another parser until it fails."""

    def __init__(
        self,
        base_parser: Parser[T],
        separator: Optional[Parser[Any]] = None,
        min: Optional[int] = None,
        max: Optional[int] = None,
    ) -> None:
        """Construct a repeat parser."""
        self.base_parser = base_parser
        self.separator_parser = separator
        self.min = min
        self.max = max

    def _parse_impl(self, data: str, offset: int) -> ParseResult[list[T]]:
        results: list[T] = []
        while True:
            try:
                if self.separator_parser is not None and results:
                    sep_result = self.separator_parser._parse(data, offset)
                    offset = sep_result.new_offset
                result = self.base_parser._parse(data, offset)
                offset = result.new_offset
                if result.result is not None:
                    results.append(result.result)
                if self.max is not None and len(results) == self.max:
                    break
            except ParseException:
                break
        if self.min is not None and len(results) < self.min:
            raise ParseException("Expected more repetitions")
        return ParseResult(results, offset)


class FunctionParser(Generic[S, T], Parser[T]):
    """Wraps another parser with a post parse function."""

    def __init__(self, base_parser: Parser[S], post_parse: Callable[[S], T]) -> None:
        """Wrap another parser."""
        self.base_parser = base_parser
        self.post_parse = post_parse

    def _parse_impl(self, data: str, offset: int) -> ParseResult[T]:
        result = self.base_parser._parse(data, offset)
        try:
            return ParseResult(self.post_parse(result.result), result.new_offset)
        except Exception:
            raise ParseException("Post-parse function failed.")


class Pair(Parser[tuple[S, T]]):
    """Run a pair of parsers one after another (stronger typed than series)."""

    def __init__(self, parser1: Parser[S], parser2: Parser[T]) -> None:
        """Construct a new pair parser."""
        self.parser1 = parser1
        self.parser2 = parser2

    def _parse_impl(self, data: str, offset: int) -> ParseResult[tuple[S, T]]:
        result1 = self.parser1._parse(data, offset)
        result2 = self.parser2._parse(data, result1.new_offset)

        return ParseResult((result1.result, result2.result), result2.new_offset)


class Series(Parser[list[T]]):
    """Runs multiple parsers after one another."""

    def __init__(
        self, *parsers: Parser[T], separator: Optional[Parser[Any]] = None
    ) -> None:
        """Construct a series parser."""
        self.parsers = parsers
        self.separator_parser = separator

    def _parse_impl(self, data: str, offset: int) -> ParseResult[list[T]]:
        results: list[T] = []
        for parser in self.parsers:
            if self.separator_parser is not None and results:
                sep_result = self.separator_parser._parse(data, offset)
                offset = sep_result.new_offset
            result = parser._parse(data, offset)
            offset = result.new_offset
            if result.result is not None:
                results.append(result.result)
        return ParseResult(results, offset)


def String(
    allowed_chars: Optional[str] = None, illegal_chars: str = "\n"
) -> Parser[str]:
    """Create a parser to parse a string."""
    return FunctionParser(Repeat(Char(allowed_chars, illegal_chars)), "".join)


def Int(base: int = 10, padding: str = "") -> Parser[int]:
    """Create a parser to parse an integer."""
    return FunctionParser(
        Pair(
            String(allowed_chars=padding),
            String(allowed_chars=string.digits),
        ),
        lambda x: int(x[1].lstrip(padding), base),
    )


def Literal(lit: str) -> Parser[str]:
    """Create a parser to parse a literal."""
    return FunctionParser(
        Series(*[Char(allowed_chars=c, illegal_chars="") for c in lit]), "".join
    )


def Enumeration(typ: Type[T]) -> Parser[T]:
    """Create a parser to parse an enum."""
    if not issubclass(typ, Enum):
        raise Exception(f"Type {typ} is not an Enum")
    return FunctionParser(Word, lambda x: typ[x])  # type: ignore


def DataClass(typ: Type[T], parser: Parser[list[Any]]) -> Parser[T]:
    """Create a parser to parse a dataclass."""
    return FunctionParser(parser, lambda x: typ(*x))


def IgnoreNewline(parser: Parser[T]) -> Parser[T]:
    """Create a parser that ignores a newline at the end of the parser."""
    return FunctionParser(Pair(parser, NewLine), lambda x: x[0])


def Suppress(parser: Parser[T]) -> Parser[None]:
    """Create a parser that suppresses the output of another parser."""
    return FunctionParser(parser, lambda x: None)


NewLine = Char(allowed_chars="\n", illegal_chars="")
Word = String(allowed_chars=string.ascii_letters)
Line: Parser[str] = IgnoreNewline(String())
Lines = Repeat(Line)
IntLine = FunctionParser(Line, int)
IntLines = Repeat(IntLine)
Point2D: Parser[Point2DObj] = FunctionParser(
    Series(Int(), Literal(","), Int()), lambda x: Point2DObj(x[0], x[2])
)


def parse(
    parser: Parser[T],
) -> Callable[[Callable[[T], ProblemResult]], Callable[[TextIO], ProblemResult]]:
    """Decorate function to produce a function that accepts a file."""

    def func(func: Callable[[T], ProblemResult]) -> Callable[[TextIO], ProblemResult]:
        def file_reader(file: TextIO) -> ProblemResult:
            problem_input = parser.parse_file(file)
            return func(problem_input)

        return file_reader

    return func
