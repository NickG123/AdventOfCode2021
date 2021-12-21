"""Day 21."""

from functools import cache
from itertools import product

import utils.parser as pc
from result import Result

# Effectively, each player moves this distance, repeating
p1_movements = [6, 4, 2, 0, 8]
p2_movements = [5, 3, 1, 9, 7]


class Player:
    """A class to hold a player."""

    def __init__(self, start_pos: int, movements: list[int]) -> None:
        """Initialize a player at a starting position."""
        self.start_pos = start_pos
        self.pos = start_pos
        self.movements = movements
        self.movement_offset = 0

        # After 10 moves, a player should be back where they started
        # They will always score the same number of points every 10 moves
        # self.ten_move_score = 0
        self.ten_move_score = sum(self.move() for _ in range(10))
        assert self.pos == start_pos
        assert self.movement_offset == 0

    def reset(self) -> None:
        """Reset the player back to default."""
        self.pos = self.start_pos
        self.movement_offset = 0

    def move(self) -> int:
        """Move the player one roll."""
        roll = self.movements[self.movement_offset]
        self.pos = (self.pos + roll - 1) % 10 + 1
        self.movement_offset = (self.movement_offset + 1) % len(self.movements)
        return self.pos

    def find_finishing_roll_num(self, target: int) -> int:
        """Determine which roll this player will reach target on."""
        num_ten_moves, score_left = divmod(target, self.ten_move_score)
        score = 0
        moves = 0
        while score < score_left:
            moves += 1
            score += self.move()
        assert moves < 10
        return num_ten_moves * 10 + moves

    def score_after_moves(self, num_moves: int) -> int:
        """Determine the score this playter will have after a number of moves."""
        num_ten_moves, moves_left = divmod(num_moves, 10)
        last_roles_score = sum(self.move() for _ in range(moves_left))
        return self.ten_move_score * num_ten_moves + last_roles_score


def run_game(p1: Player, p2: Player, target: int) -> int:
    """Find the winner and loser of the game."""
    [p1_finish, p2_finish] = [p.find_finishing_roll_num(target) for p in [p1, p2]]
    if p1_finish <= p2_finish:
        winner_finish = p1_finish
        loser_finish = p1_finish - 1
        loser = p2
    else:
        winner_finish = p2_finish
        loser_finish = p2_finish
        loser = p1
    loser.reset()
    loser_score = loser.score_after_moves(loser_finish)
    return loser_score * (loser_finish + winner_finish) * 3


def tuple_replace(tuple: tuple[int, int], val: int, offset: int) -> tuple[int, int]:
    """Replace the value at an offset in a tuple."""
    return (val, tuple[1]) if offset == 0 else (tuple[0], val)


@cache
def part2(
    positions: tuple[int, int],
    player: int = 0,
    scores: tuple[int, int] = (0, 0),
) -> tuple[int, int]:
    """Run the game with the quantum dice."""
    other_player = 1 - player
    p1_wins = 0
    p2_wins = 0
    if scores[other_player] >= 21:
        return tuple_replace((0, 0), 1, other_player)
    for roll_result in product([1, 2, 3], repeat=3):
        new_position = (positions[player] + sum(roll_result) - 1) % 10 + 1
        new_score = scores[player] + new_position
        p1_sub_wins, p2_sub_wins = part2(
            tuple_replace(positions, new_position, player),
            other_player,
            tuple_replace(scores, new_score, player),
        )
        p1_wins += p1_sub_wins
        p2_wins += p2_sub_wins
    return (p1_wins, p2_wins)


StartingPosition = pc.IgnorePrefix(
    pc.Pair(
        pc.Series(pc.Literal("Player "), pc.Int(), pc.Literal(" starting position: ")),
        pc.Int(),
    )
)
StartingPositions = pc.Pair(StartingPosition, StartingPosition, separator=pc.NewLine)


@pc.parse(StartingPositions)
def run(starting_positions: tuple[int, int]) -> Result:
    """Solution for Day 21."""
    p1 = Player(starting_positions[0], p1_movements)
    p2 = Player(starting_positions[1], p2_movements)

    part1 = run_game(p1, p2, 1000)

    return Result(part1, max(part2(starting_positions)))
