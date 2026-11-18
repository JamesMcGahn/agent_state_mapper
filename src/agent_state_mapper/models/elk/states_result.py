from dataclasses import dataclass
from ..intra import State
from datetime import datetime


@dataclass(frozen=True)
class StatesResult:
    start: datetime
    end: datetime
    states: list[State]
