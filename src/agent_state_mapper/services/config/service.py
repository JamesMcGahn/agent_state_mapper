from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Any, TypeVar

if TYPE_CHECKING:
    from ...cli import CLI
    from .app_config import AppConfig
    from ..file import TomlFileService
    from .state_config import StateConfig
    from ...models.states import ProviderStates

from .app_config import AppConfig
from ...models.config import AppSettings, StateSettings
from ...errors import ConfigError
from tomllib import TOMLDecodeError

T = TypeVar("T")


class ConfigService:

    def __init__(
        self,
        cli: CLI,
        toml_file_service: TomlFileService,
        app_config: AppConfig,
        state_config: StateConfig,
    ):
        self._cli = cli
        self._app_config = app_config
        self._toml_file_service = toml_file_service
        self._state_config = state_config

    def get_app_config(self) -> AppSettings:
        return self._app_config.app_settings

    def get_state_config(self) -> StateSettings:
        return self._state_config.state_settings

    def load_application_config(self):
        default_path = self._app_config.get_default_config(
            folder="app", file_name="default_config.toml"
        )
        config_path = self._app_config.get_config_path(
            folder="app", file_name="app_config.toml", default_config=default_path
        )

        raw_config = self._toml_file_service.read(config_path=config_path)
        self._app_config.apply_config(raw_config)

    def load_state_configs(self):
        common_config = self.load_state_common_config()
        provider_configs = self.load_state_provider_config()

        self._state_config.state_settings = StateSettings(
            common=common_config,
            providers=provider_configs,
        )

    def load_state_common_config(self):
        return self._load_state_helper(
            "common.toml", self._state_config.parse_common_config
        )

    def load_state_provider_config(self) -> list[ProviderStates]:
        providers_files = ("avaya.toml",)
        providers = []
        for provider in providers_files:
            provider_dc = self._load_state_helper(
                provider, self._state_config.parse_provider_config
            )
            providers.append(provider_dc)
        return providers

    def _load_state_helper(
        self, file_name: str, parse_fn: Callable[[dict[str, Any], str], T]
    ) -> T:
        external_path = self._state_config.get_external_config_path(
            "states", file_name=file_name
        )
        default_path = self._app_config.get_default_config(
            "states", file_name=file_name
        )
        data_class = None
        try:
            raw_config = self._toml_file_service.read(external_path)
            data_class = parse_fn(raw_config, file_name)
            self._cli.print_status(
                f"Loading state config: {file_name} from external file: {external_path}"
            )
        except ConfigError, OSError, FileNotFoundError, TOMLDecodeError:
            self._cli.print_status(f"Loading provider {file_name} config from default.")
            raw_config = raw_config = self._toml_file_service.read(
                config_path=default_path
            )

            if external_path.is_file():
                problem_path = external_path.with_name(f"problem_{file_name}")
                external_path.rename(problem_path)
                self._cli.print_warn(f"Renamed problem file as {problem_path.name}")
            self._toml_file_service.write(raw_config, external_path)
            data_class = parse_fn(raw_config, file_name)
        self._cli.print_status(f"State config: {file_name} Successfully Loaded.")
        return data_class
