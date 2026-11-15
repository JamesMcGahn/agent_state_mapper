from pathlib import Path
import sys
import tomllib
from .cli import CLI
from .errors import ConfigError
from .models.intra import Node
from dataclasses import fields


class AppConfig:
    def __init__(self, cli: CLI):
        self.cli = cli
        self._node_list = []

    @property
    def node_list(self) -> list[Node]:
        return self._node_list

    def get_default_config(
        self,
    ) -> Path:
        return Path(__file__).resolve().with_name("default_config.toml")

    def get_config_path(self, external_dir: Path | None = None) -> Path:
        if external_dir is None:
            if getattr(sys, "frozen", False):
                external_dir = Path(sys.executable).resolve().parent
            else:
                external_dir = Path(__file__).resolve().parents[2]

        external_config = external_dir / "config.toml"

        path = None
        if external_config.exists():
            path = external_config
            self.cli.print_status(f"Loading config from external file: {path}")

        else:
            self.cli.print_status("Loading Config from default config.")
            path = self.get_default_config()

        return path

    def load_config(self, config_path: Path | None = None) -> None:
        if config_path is None:
            config_path = self.get_config_path()
        elif not config_path.is_file():
            msg = "Config file does NOT exist."
            self.cli.print_error(msg)
            raise ConfigError(msg)

        with config_path.open("rb") as file:
            config = tomllib.load(file)

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
