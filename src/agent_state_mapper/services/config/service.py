from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...cli import CLI
    from .app_config import AppConfig

from .app_config import AppConfig
from ...models.config import AppSettings


class ConfigService:

    def __init__(self, cli: CLI, app_config: AppConfig):
        self.cli = cli
        self._app_config = app_config

    def get_app_config(self):
        return AppSettings(nodes=self._app_config.node_list)

    def load_application_config(self):
        default_path = self._app_config.get_default_config(
            folder="app", file_name="default_config.toml"
        )
        config_path = self._app_config.get_config_path(
            folder="app", file_name="app_config.toml", default_config=default_path
        )
        self._app_config.load_config(config_path=config_path)
