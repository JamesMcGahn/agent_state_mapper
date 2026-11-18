from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import CLI

from ...cli import CLI
from ...errors import ConfigError
from ...models.intra import Node
from dataclasses import fields
from .base_config import BaseConfig


class AppConfig(BaseConfig):
    def __init__(self, cli: CLI):
        super().__init__(cli)
        self._node_list = []

    @property
    def node_list(self) -> list[Node]:
        return self._node_list

    def load_config_helper(self, config: dict[str, Any]) -> None:
        nodes: dict[str, str] = config.get("nodes")
        if not nodes or nodes is None:
            msg = "Config file doesn't have any nodes. Make sure to write the nodes like [nodes.Node3]"
            self.cli.print_error(msg)
            raise ConfigError(msg)

        nodes_list = []

        required = {field.name for field in fields(Node)} - {"name"}

        for node_name, node_settings in nodes.items():
            if not isinstance(node_settings, dict):
                msg = "Config file is formatted improperly."
                raise ConfigError(msg)

            missing = required - node_settings.keys()
            unknown = node_settings.keys() - required
            if missing:
                msg = f"{node_name} is missing the {", ".join(missing)} in the config file. Skipping Node..."
                self.cli.print_error(msg)
                continue

            if unknown:
                msg = f"{node_name} is has unexpected key(s) {", ".join(unknown)} in the config file. Skipping Node..."
                self.cli.print_error(msg)
                continue

            blank_fields = [
                key
                for key, value in node_settings.items()
                if isinstance(value, str) and not value.strip()
            ]

            if blank_fields:
                self.cli.print_error(
                    f"{node_name} has blank fields: {', '.join(blank_fields)}"
                )
                continue

            nodes_list.append(Node(name=node_name, **node_settings))

        if not nodes_list:
            msg = "Failed to load config file. No Nodes exist."
            raise ConfigError(msg)
        self.cli.print_status("Config succesfully loaded.")
        self._node_list = nodes_list
