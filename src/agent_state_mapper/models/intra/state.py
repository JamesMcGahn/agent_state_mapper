from dataclasses import dataclass, field


@dataclass(frozen=True)
class State:
    state: str
    aux: str
    original_mapping: str = field(default="", compare=False)
