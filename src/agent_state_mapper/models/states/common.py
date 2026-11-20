from dataclasses import dataclass


@dataclass
class CommonStates:
    legacy_states: dict[str, str]
    exact_aux_matches: dict[str, str]
    aux_keywords: dict[str, str]
