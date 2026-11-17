from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...enums import PROVIDER_CATEGORY
from dataclasses import dataclass


@dataclass
class Provider:
    name: str
    guid: str
    guid_underscored: str
    provider_category: PROVIDER_CATEGORY
    provider_type: str
