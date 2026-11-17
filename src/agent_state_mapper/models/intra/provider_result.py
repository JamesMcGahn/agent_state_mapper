from dataclasses import dataclass
from .provider import Provider


@dataclass
class ProviderResult:
    acd_providers: list[Provider]
    intra_call_provider: Provider | None
