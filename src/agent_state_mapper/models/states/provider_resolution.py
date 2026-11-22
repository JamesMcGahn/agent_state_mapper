from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..intra.provider import Provider
    from .provider import ProviderStates
    from ...enums import PROVIDER_MATCH_BY


from dataclasses import dataclass


@dataclass
class ProviderResolution:
    provider: Provider
    config: ProviderStates | None
    matched_by: PROVIDER_MATCH_BY
    matched_states: set[str]
    unexpected_states: set[str]
    needs_review: bool
    match_percentage: float
