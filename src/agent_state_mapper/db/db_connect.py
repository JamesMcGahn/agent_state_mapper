from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, Any

if TYPE_CHECKING:
    from ..models.db import DBSettings
    from ..cli import CLI
from abc import ABC, abstractmethod

CursorT = TypeVar("CursorT")


class DBConnect(ABC, Generic[CursorT]):

    def __init__(self, cli: CLI):
        self._cli = cli
        self.connection = None

    @abstractmethod
    def connect(self, settings: DBSettings):
        pass

    @abstractmethod
    def execute_query(self, query, params=None) -> CursorT:
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def fetch_all(
        self, query, params: tuple[Any, ...] | None = None
    ) -> tuple[Any, ...] | None:
        pass

    @abstractmethod
    def fetch_one(
        self, query, params: tuple[Any, ...] | None = None
    ) -> tuple[Any, ...] | None:
        pass
