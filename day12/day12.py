"""Day 12."""

from dataclasses import dataclass, field

import utils.parser as pc
from result import Result


@dataclass
class Node:
    """Represents a node in the graph."""

    name: str
    connections: set[str] = field(default_factory=set)

    @property
    def is_small(self) -> bool:
        """Check if this node is a small cave."""
        return self.name.islower()

    @property
    def is_large(self) -> bool:
        """Check if this node is a large cave."""
        return self.name.isupper()

    def __hash__(self) -> int:
        """Hash the node."""
        return hash(self.name)


class Traverser:
    """A traverser that computes paths in a grid."""

    def __init__(self, nodes: dict[str, Node]) -> None:
        """Construct a new grid traverser."""
        self.nodes = nodes
        self.memo: dict[tuple[Node, frozenset[Node], bool], list[list[Node]]] = {}

    def traverse(
        self,
        current_node: Node,
        path: list[Node],
        hit_small_twice: bool,
    ) -> list[list[Node]]:
        """Recursive function to find all paths in the graph."""
        visited_small_caves = frozenset(n for n in path if n.is_small)

        memo_key = (
            current_node,
            visited_small_caves,
            hit_small_twice,
        )
        if memo_key in self.memo:
            return self.memo[memo_key]

        path_copy = list(path)
        path_copy.append(current_node)

        if current_node.name == "end":
            return [path_copy]

        results = []

        for node_name in current_node.connections:
            neighbour = self.nodes[node_name]
            if neighbour not in visited_small_caves:
                results.extend(self.traverse(neighbour, path_copy, hit_small_twice))
            elif not hit_small_twice and neighbour.name != "start":
                results.extend(self.traverse(neighbour, path_copy, True))

        self.memo[memo_key] = results
        return results


@pc.parse(
    pc.Repeat(
        pc.Series(pc.Word, pc.Suppress(pc.Literal("-")), pc.Word),
        separator=pc.NewLine,
    )
)
def run(connections: list[list[str]]) -> Result:
    """Solution for Day 12."""
    nodes: dict[str, Node] = {}
    for start, end in connections:
        for node_name in [start, end]:
            if node_name not in nodes:
                nodes[node_name] = Node(node_name)
        nodes[start].connections.add(end)
        nodes[end].connections.add(start)

    traverser = Traverser(nodes)

    part1 = len(traverser.traverse(nodes["start"], [], True))
    part2 = len(traverser.traverse(nodes["start"], [], False))

    return Result(part1, part2)
