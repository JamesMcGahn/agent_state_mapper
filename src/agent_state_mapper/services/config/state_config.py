from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import CLI

from ...cli import CLI
from ...errors import ConfigError
from ...models.states import CommonStates, ProviderStates
from ...models.config import StateSettings
from dataclasses import fields
from .base_config import BaseConfig
from ...models.base import DataclassInstance


class StateConfig(BaseConfig):
    def __init__(self, cli: CLI):
        super().__init__(cli)
        self._state_config = None
        self._alias_set = set()

    @property
    def state_settings(self) -> StateSettings:
        return self._state_config

    @state_settings.setter
    def state_settings(self, settings: StateSettings) -> StateSettings:
        self._state_config = settings

    def clear_alias_set(self):
        self._alias_set = set()

    def parse_common_config(
        self, config: dict[str, Any], file_name: str
    ) -> CommonStates:
        self._check_raise_missing_keys(config, CommonStates, file_name)

        return CommonStates(
            legacy_states=config["legacy_states"],
            exact_aux_matches=config["exact_aux_matches"],
            aux_keywords=config["aux_keywords"],
        )

    def parse_provider_config(
        self, config: dict[str, Any], file_name: str
    ) -> ProviderStates:
        self._check_raise_missing_keys(
            config, ["provider", "states", "state_aux_mappings"], file_name
        )

        self._check_raise_missing_keys(
            config["provider"], ["name", "aliases", "base_states"], file_name
        )

        provider = config["provider"]
        state_aux_mappings = config["state_aux_mappings"]
        if not isinstance(state_aux_mappings, list):
            msg = f"state_aux_mappings passed as type {type(state_aux_mappings)} and needs to be a list."
            self._cli.print_error(msg)
            raise ConfigError(msg)

        aux_mappings = {}
        for mapping in state_aux_mappings:
            try:
                self._check_raise_missing_keys(
                    mapping, ["state", "aux", "target"], file_name
                )
                aux_mappings[(mapping["state"], mapping["aux"])] = mapping["target"]
            except Exception:
                self._cli.print_warn(f"Skipping Aux Mapping from {file_name}")
                continue

        self._check_aliases(config["provider"], file_name)

        return ProviderStates(
            name=provider["name"],
            aliases=provider["aliases"],
            base_states=provider["base_states"],
            states=config["states"],
            state_aux_mappings=aux_mappings,
        )

    def _check_aliases(self, config: dict[str, Any], file_name: str):
        aliases = config["aliases"]
        if not isinstance(aliases, list):
            msg = f"Config passed as 'aliases' {type(config)} for {file_name}. aliases must be a list."
            self._cli.print_error(msg)
            raise ConfigError(msg)

        provider_alias_no_match = set()

        for alias in aliases:
            if alias in self._alias_set:
                msg = f"Config passed {alias} in aliases for {file_name} but alias already used for a different config."
                self._cli.print_error(msg)
                raise ConfigError(msg)
            provider_alias_no_match.add(alias)

        self._alias_set.update(provider_alias_no_match)

    def _check_raise_missing_keys(
        self,
        config: dict[str, Any],
        fields_source: DataclassInstance | list[str],
        file_name: str,
    ) -> None:
        if not isinstance(config, dict):
            raise ConfigError(f"Config passed as {type(config)} for {file_name}")

        if isinstance(fields_source, list):
            missing = [
                config_key for config_key in fields_source if config_key not in config
            ]
        else:
            missing = [
                config_key.name
                for config_key in fields(fields_source)
                if config_key.name not in config
            ]

        if missing:
            msg = f"{",".join(missing)} missing from states {file_name}."
            self._cli.print_error(msg)
            raise ConfigError(msg)
