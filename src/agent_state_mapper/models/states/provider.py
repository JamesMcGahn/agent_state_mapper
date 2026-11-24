from dataclasses import dataclass


@dataclass
class ProviderStates:
    name: str
    aliases: list[str]
    base_states: list[str]
    on_call_states: list[str]
    states: dict[str, str]
    state_aux_mappings: dict[tuple[str, str], str]
