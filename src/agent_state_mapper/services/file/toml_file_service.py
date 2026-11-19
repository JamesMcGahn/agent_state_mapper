from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agent_state_mapper.cli import CLI


from pathlib import Path
import toml
import tomllib

from .base_write import BaseWrite


class TomlFileService(BaseWrite):

    def __init__(self, cli: CLI):
        super().__init__(cli)

    def read(self, config_path: Path) -> dict[str, Any]:
        if not config_path.is_file():
            msg = f"Config file does NOT exist. {config_path}"
            self._cli.print_error(msg)
            raise OSError(msg)

        with config_path.open("rb") as file:
            config = tomllib.load(file)
            return config

    def write(self, data: dict[str, Any], output_path: str | Path) -> Path:
        try:
            output_path = self.get_output_path(output_path, file_ext=".json")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding="utf-8") as file:
                toml.dump(data, file)
            message = f"File Successfully saved {output_path}"
            self._cli.print_status(message)
            return output_path
        except OSError:
            message = f"Could not save the file {output_path}"
            self._cli.print_error(message)
            raise
        except Exception:
            message = f"Unexpected error saving the file {output_path}"
            self._cli.print_error(message)
            raise
