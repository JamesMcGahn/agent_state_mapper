from dataclasses import dataclass
from ..intra import Node


@dataclass(frozen=True)
class AppSettings:
    nodes: list[Node]
