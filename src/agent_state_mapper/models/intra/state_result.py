from dataclasses import dataclass
from .provider import Provider
from .state import State


@dataclass
class StateResult:
    provider: Provider
    states: list[State]
