from dataclasses import dataclass, field
from ..intra import Node


@dataclass(frozen=True)
class AppSettings:
    nodes: list[Node] = field(default_factory=list)
