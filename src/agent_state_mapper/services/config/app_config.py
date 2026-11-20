from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import CLI

from ...cli import CLI
from ...errors import ConfigError
from ...models.intra import Node
from ...models.config import AppSettings
from dataclasses import fields
from .base_config import BaseConfig


class AppConfig(BaseConfig):
    def __init__(self, cli: CLI):
        super().__init__(cli)
        self._node_list = []
        self._app_config = AppSettings()

    @property
    def app_settings(self) -> AppSettings:
        return self._app_config

    def apply_config(self, config):
        self._node_list = self.parse_config(config)
        self._app_config = AppSettings(nodes=self._node_list)

    def parse_config(self, config: dict[str, Any]) -> list[Node]:
        nodes: dict[str, str] = config.get("nodes")
        if not nodes or nodes is None:
            msg = "App config file doesn't have any nodes. Make sure to write the nodes like [nodes.Node3]"
            self._cli.print_error(msg)
            raise ConfigError(msg)

        nodes_list = []

        required = {field.name for field in fields(Node)} - {"name"}

        for node_name, node_settings in nodes.items():
            if not isinstance(node_settings, dict):
                msg = "App config file is formatted improperly."
                raise ConfigError(msg)

            missing = required - node_settings.keys()
            unknown = node_settings.keys() - required
            if missing:
                msg = f"{node_name} is missing the {", ".join(missing)} in the app config file. Skipping Node..."
                self._cli.print_error(msg)
                continue

            if unknown:
                msg = f"{node_name} is has unexpected key(s) {", ".join(unknown)} in the app config file. Skipping Node..."
                self._cli.print_error(msg)
                continue

            blank_fields = [
                key
                for key, value in node_settings.items()
                if isinstance(value, str) and not value.strip()
            ]

            if blank_fields:
                self._cli.print_error(
                    f"{node_name} has blank fields: {', '.join(blank_fields)}"
                )
                continue

            nodes_list.append(Node(name=node_name, **node_settings))

        if not nodes_list:
            msg = "Failed to load app config file. No Nodes exist."
            raise ConfigError(msg)
        self._cli.print_status("App config succesfully loaded.")
        return nodes_list
