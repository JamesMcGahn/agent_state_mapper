from dataclasses import dataclass
from ..states import CommonStates, ProviderStates


@dataclass(frozen=True)
class StateSettings:
    common: CommonStates
    providers: list[ProviderStates]
