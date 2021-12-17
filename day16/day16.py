"""Day 16."""

import math
import operator
from dataclasses import dataclass
from enum import Enum
from typing import Callable

import utils.parser as pc
from result import Result


class PacketType(Enum):
    """Packet types."""

    SUM = 0
    PRODUCT = 1
    MINIMUM = 2
    MAXIMUM = 3
    LITERAL = 4
    GREATER_THAN = 5
    LESS_THAN = 6
    EQUAL = 7


OpType = Callable[[list[int]], int]


def bin_op(op: Callable[[int, int], int]) -> OpType:
    """Convert a binary operator into an operator that acts on a list of length 2."""

    def sub_function(numbers: list[int]) -> int:
        assert len(numbers) == 2
        [a, b] = numbers
        return op(a, b)

    return sub_function


OPERATORS: dict[PacketType, OpType] = {
    PacketType.SUM: sum,
    PacketType.PRODUCT: math.prod,
    PacketType.MINIMUM: min,
    PacketType.MAXIMUM: max,
    PacketType.GREATER_THAN: bin_op(operator.gt),
    PacketType.LESS_THAN: bin_op(operator.lt),
    PacketType.EQUAL: bin_op(operator.eq),
}


def create_mask(start: int, end: int) -> int:
    """Create a bitmask that only includes values between start and end."""
    top = (1 << start) - 1
    bottom = (1 << end) - 1
    return top - bottom


@dataclass
class ParseResult:
    """Holds the result of a packet parse."""

    total_version_number: int
    result: int


class PacketParser:
    """A class for parsing bits out of bytes."""

    def __init__(self, data: bytes) -> None:
        """Construct a new bitparser."""
        self.data = data
        self.bit_offset = 0

    def read_number(self, bits: int) -> int:
        """Read a number out of the bytes."""
        new_bit_offset = self.bit_offset + bits

        start_byte = self.bit_offset // 8
        stop_byte = (
            new_bit_offset // 8 if new_bit_offset % 8 != 0 else new_bit_offset // 8 - 1
        )

        bits_before_in_first_byte = 8 - (self.bit_offset % 8)
        bits_after_in_last_byte = (8 - new_bit_offset) % 8

        result = 0

        for byte_offset, byte in enumerate(self.data[start_byte : stop_byte + 1]):
            current_byte = byte_offset + start_byte
            byte_val = byte
            if current_byte == start_byte:
                byte_val &= create_mask(bits_before_in_first_byte, 0)
            if current_byte == stop_byte:
                byte_val &= create_mask(8, bits_after_in_last_byte)
                byte_val >>= bits_after_in_last_byte
            else:
                byte_val <<= (stop_byte - current_byte) * 8 - bits_after_in_last_byte

            result += byte_val

        self.bit_offset = new_bit_offset
        return result

    def parse_packet(self) -> ParseResult:
        """Parse a packet."""
        packet_version = self.read_number(3)
        packet_type = PacketType(self.read_number(3))

        if packet_type == PacketType.LITERAL:
            literal = self.parse_literal()
            return ParseResult(packet_version, literal)
        else:

            length_type = self.read_number(1)
            op = OPERATORS[packet_type]

            if length_type == 0:
                sub_packet_length = self.read_number(15)
                end_position = self.bit_offset + sub_packet_length
                subparse_result = self.parse_subpackets(
                    lambda offset, _: offset == end_position, op
                )
            else:
                num_sub_packets = self.read_number(11)
                subparse_result = self.parse_subpackets(
                    lambda _, parsed: parsed == num_sub_packets, op
                )
            return ParseResult(
                subparse_result.total_version_number + packet_version,
                subparse_result.result,
            )

    def parse_literal(self) -> int:
        """Parse a literal."""
        result = 0
        while self.read_number(1):
            result += self.read_number(4)
            result <<= 4
        result += self.read_number(4)
        return result

    def parse_subpackets(
        self, stop: Callable[[int, int], bool], op: OpType
    ) -> ParseResult:
        """Parse subpackets until sub_packet_length bits have been parsed."""
        total_version_number = 0
        results = []
        parsed_packets = 0

        while True:
            subparse_result = self.parse_packet()
            total_version_number += subparse_result.total_version_number
            results.append(subparse_result.result)
            parsed_packets += 1
            if stop(self.bit_offset, parsed_packets):
                return ParseResult(total_version_number, op(results))


@pc.parse(pc.HexString(pc.String()))
def run(data: bytes) -> Result:
    """Solution for Day 16."""
    parser = PacketParser(data)
    result = parser.parse_packet()
    return Result(result.total_version_number, result.result)
