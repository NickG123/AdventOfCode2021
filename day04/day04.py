"""Day 04."""

from typing import Iterable

import utils.parser as pc
from result import Result
from utils.geometry import SizedGrid2D


class Bingo:
    """A bingo grid."""

    def __init__(self, data: list[list[int]]) -> None:
        """Create a new bingo card."""
        self.number_grid = SizedGrid2D.from_data(data, reverse_lookup=True)
        self.calls: SizedGrid2D[bool] = SizedGrid2D.from_data(
            [[False] * len(data[0]) for _ in data]
        )
        self.won = False

    def add_call(self, call: int) -> None:
        """Add a call to the card."""
        pos = self.number_grid.find(call)
        if pos is not None:
            self.calls[pos] = True

            if all(self.calls.row(pos.y)) or all(self.calls.col(pos.x)):
                self.won = True

    @property
    def unmarked_sum(self) -> int:
        """Get the sum of the unmarked cells of the bingo card."""
        total = 0
        for num, call in zip(self.number_grid.cells, self.calls.cells):
            if not call:
                total += num
        return total


def get_winning_card_and_call(
    cards: set[Bingo], calls: Iterable[int]
) -> tuple[Bingo, int]:
    """Get the winning card and call."""
    for call in calls:
        for card in cards:
            card.add_call(call)
            if card.won:
                return (card, call)
    raise Exception("No winning card found after moves completed.")


CallsParser = pc.IgnoreNewline(pc.Repeat(pc.Int(), separator=pc.Literal(",")))
BoardLine = pc.Repeat(pc.Int(padding=" "), separator=pc.Literal(" "), min=1)
Board = pc.Repeat(BoardLine, separator=pc.NewLine)
Boards = pc.Repeat(Board, separator=pc.NewLine)


@pc.parse(pc.Pair(pc.IgnoreNewline(CallsParser), Boards))
def run(input_data: tuple[list[int], list[list[list[int]]]]) -> Result:
    """Solution for Day 04."""
    calls, card_groups = input_data

    cards = {Bingo(card) for card in card_groups}

    winning_card, winning_call = get_winning_card_and_call(cards, calls)
    cards.remove(winning_card)

    while len(cards) > 1:
        card, _ = get_winning_card_and_call(cards, calls)
        cards.remove(card)
    losing_card, losing_call = get_winning_card_and_call(cards, calls)

    return Result(
        winning_card.unmarked_sum * winning_call, losing_card.unmarked_sum * losing_call
    )
