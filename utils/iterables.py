"""Helper utilities related to iterables."""
import operator
from itertools import groupby
from typing import Iterable, TypeVar

T = TypeVar("T")
S = TypeVar("S")


def group_as_set(it: Iterable[tuple[S, T]]) -> dict[S, set[T]]:
    """Group a list of key/value pairs by key.

    Take an iterable of key/value pairs with potentially duplicated keys and
    produce a mapping of unique key to set of values associated with that key
    """
    return {
        k: {val for _, val in g}
        for k, g in groupby(sorted(it), key=operator.itemgetter(0))
    }
