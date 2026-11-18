from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...cli import CLI
from time import monotonic, sleep


class NetworkThrottle:
    """Class to throttle requests. Throttle will delay requests based on time of the last request.
    params:
    interval: time between requests in seconds
    """

    def __init__(self, cli: CLI, interval: float = 0.5):
        super().__init__()
        self._cli = cli
        self._base_interval = interval
        self._interval = interval
        self._last_call = 0.0

    def wait(self):
        elapsed = monotonic() - self._last_call
        if elapsed < self._interval:
            wait_time = self._interval - elapsed
            sleep(wait_time)
        self._last_call = monotonic()

    def set_wait_interval(self, interval: float) -> None:
        self._interval = interval

    def increase_wait_interval(self, amount: float = 0.5) -> None:
        self._interval += amount

        self._cli.print_info(
            f"Throttle interval increased to {self._interval:.3f}s",
        )

    def delay(self, amount: float) -> None:
        self._cli.print_info(
            f"Server requested retry delay of {amount:.3f}s. Waiting...",
        )

        sleep(amount)

    def reset_wait_interval(self) -> None:
        self._interval = self._base_interval
