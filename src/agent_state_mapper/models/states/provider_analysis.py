from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..intra.provider import Provider
    from ..elk import StatesResult
    from .provider_resolution import ProviderResolution

from dataclasses import dataclass


@dataclass
class ProviderAnalysis:
    provider: Provider
    observed_states: StatesResult
    resolution: ProviderResolution | None
