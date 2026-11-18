from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..network.network_throttle import NetworkThrottle
    from ..network.network_client import NetworkClient
    from ...cli import CLI
from ..network.base_api import BaseApi
from ...enums import HTTPMETHOD
from ...models.network import NetworkRequest
from ...models.intra import TenantSelection, Provider, State
from datetime import datetime, timedelta, timezone
from time import monotonic
from ...models.elk import StatesResult


class ELKAPI(BaseApi):

    def __init__(
        self,
        cli: CLI,
        network_client: NetworkClient,
        network_throttle: NetworkThrottle,
    ):
        super().__init__(network_client, network_throttle)
        self._cli = cli

    def get_acd_state(
        self,
        tenant_selection: TenantSelection,
        provider_instance: Provider,
        day_range: int = 7,
    ) -> list[StatesResult]:
        if day_range <= 0:
            self._cli.print_error(
                f"{__class__.__name__}: day_range must be greater than zero"
            )
            raise ValueError("day_range must be greater than zero")
        node = tenant_selection.node
        url = f"{node.elk_endpoint.strip()}/_search"
        request_headers = {
            "Content-Type": "application/json",
            "Authorization": f"ApiKey {node.elk_api_key.strip()}",
        }

        end_time_utc = datetime.now(timezone.utc)
        start_time_utc = end_time_utc - timedelta(days=day_range)

        states_in_range: list[StatesResult] = []
        self._cli.print_status(
            f"Requesting State Data from ELK for {provider_instance.name} - {start_time_utc:%Y-%m-%d %H:%M}-{end_time_utc:%H:%M}"
        )
        windows = list(self.hour_windows(start_time_utc, end_time_utc))
        total = len(windows)
        started = monotonic()
        self._cli.print_progress(f"ELK windows: 0/{total} (0%) | Elapsed: 00:00")
        try:
            for window_start, window_end in windows:
                request_body = {
                    "size": 0,
                    "query": {
                        "bool": {
                            "filter": [
                                {
                                    "term": {
                                        "fields.ProviderInstance": provider_instance.guid_underscored
                                    }
                                },
                                {
                                    "term": {
                                        "fields.filename": r"audit\AgentStateDetail.log"
                                    }
                                },
                                {
                                    "range": {
                                        "@timestamp": {
                                            "gte": window_start.isoformat(),
                                            "lt": window_end.isoformat(),
                                        }
                                    }
                                },
                            ]
                        }
                    },
                    "aggs": {
                        "by_state": {
                            "terms": {"field": "fields.CurrentState", "size": 1000},
                            "aggs": {
                                "by_aux": {
                                    "terms": {"field": "fields.Auxcode", "size": 1000}
                                }
                            },
                        }
                    },
                }

                request = NetworkRequest(
                    method=HTTPMETHOD.POST,
                    headers=request_headers,
                    url=url,
                    retries=1,
                    json=request_body,
                    timeout=60.0,
                )
                response = self._execute(request)

                states_for_window = self._parse_state_aggregate(response.data)
                states_in_range.append(
                    StatesResult(
                        start=window_start, end=window_end, states=states_for_window
                    )
                )
                elapsed = int(monotonic() - started)
                minutes, seconds = divmod(elapsed, 60)
                completed = len(states_in_range)
                self._cli.print_progress(
                    f"ELK windows: {completed}/{total} ({completed / total:.0%})"
                    f" | Elapsed: {minutes:02d}:{seconds:02d}"
                )
        finally:
            self._cli.end_progress()
        self._cli.print_status(
            f"Finished getting State Data from ELK for {provider_instance.name} - {start_time_utc:%Y-%m-%d %H:%M}-{end_time_utc:%H:%M}"
        )
        return states_in_range

    def hour_windows(self, start_utc: datetime, end_utc: datetime):
        t = start_utc
        while t < end_utc:
            t2 = min(t + timedelta(hours=1), end_utc)
            yield (t, t2)
            t = t2

    def _parse_state_aggregate(self, payload: dict[str, Any]) -> list[State]:
        states_in_window = []
        aggregate = payload.get("aggregations", {})
        by_state = aggregate.get("by_state", {}).get("buckets", []) or []
        for state_item in by_state:
            state = state_item.get("key")
            if state is None:
                continue
            by_aux = state_item.get("by_aux", {}).get("buckets", []) or []
            for ab in by_aux:
                aux = ab.get("key")
                states_in_window.append(
                    State(state=str(state), aux="" if aux is None else str(aux))
                )
        return states_in_window
