from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..intra import State
    from ...enums import V11_STATE, MAPPING_SOURCE

from dataclasses import dataclass


@dataclass
class StateMappingResult:
    state: State
    target: V11_STATE
    source: MAPPING_SOURCE
    needs_review: bool
    reason: str | None = None
