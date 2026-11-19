from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...cli import CLI
    from .app_config import AppConfig
    from ..file import TomlFileService

from .app_config import AppConfig
from ...models.config import AppSettings


class ConfigService:

    def __init__(
        self, cli: CLI, toml_file_service: TomlFileService, app_config: AppConfig
    ):
        self.cli = cli
        self._app_config = app_config
        self._toml_file_service = toml_file_service

    def get_app_config(self) -> AppSettings:
        return self._app_config.app_settings

    def load_application_config(self):
        default_path = self._app_config.get_default_config(
            folder="app", file_name="default_config.toml"
        )
        config_path = self._app_config.get_config_path(
            folder="app", file_name="app_config.toml", default_config=default_path
        )

        raw_config = self._toml_file_service.read(config_path=config_path)
        self._app_config.apply_config(raw_config)
