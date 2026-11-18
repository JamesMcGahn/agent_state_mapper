from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .api import ELKAPI
    from ...cli import CLI
    from ...models.intra import TenantSelection, Provider

from ...models.elk import StatesResult


class ELKService:

    def __init__(self, cli: CLI, elk_api: ELKAPI):
        self._cli = cli
        self._elk_api = elk_api

    def distinct_acd_states(
        self,
        tenant_selection: TenantSelection,
        provider_instance: Provider,
        day_range: int = 7,
    ) -> StatesResult:
        result = self._elk_api.get_acd_state(
            tenant_selection, provider_instance, day_range
        )
        distinct_pairs = set()
        window_start = None
        window_end = None
        for idx, window in enumerate(result):
            if idx == 0:
                window_start = window.start
            if idx == len(result) - 1:
                window_end = window.end
            distinct_pairs.update(window.states)

        states = list(distinct_pairs)

        return StatesResult(start=window_start, end=window_end, states=states)
