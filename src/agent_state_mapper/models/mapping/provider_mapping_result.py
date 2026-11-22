from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..states import ProviderAnalysis
    from .state_mapping_result import StateMappingResult

from dataclasses import dataclass


@dataclass
class ProviderMappingResult:
    analysis: ProviderAnalysis
    mappings: list[StateMappingResult]
