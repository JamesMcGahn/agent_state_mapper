from dataclasses import dataclass
from datetime import datetime


@dataclass
class PausedRule:
    name: str
    paused_date: datetime
