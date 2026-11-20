from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...cli import CLI


from pathlib import Path
import sys


class BaseConfig:
    def __init__(self, cli: CLI):
        self._cli = cli

    def get_default_config(self, folder: str, file_name: str) -> Path:
        package_root = Path(__file__).resolve().parents[2]
        return package_root / "default_configs" / folder / file_name

    def get_external_config_path(
        self, folder: str, file_name: str, external_dir: Path | None = None
    ) -> Path:
        if external_dir is None:
            if getattr(sys, "frozen", False):
                external_dir = Path(sys.executable).resolve().parent
            else:
                external_dir = Path(__file__).resolve().parents[4]

        return external_dir / "config" / folder / file_name

    def get_config_path(
        self,
        folder: str,
        file_name: str,
        default_config: Path,
        external_dir: Path | None = None,
    ) -> Path:

        path = None
        external_config = self.get_external_config_path(folder, file_name, external_dir)
        if external_config.exists():
            path = external_config
            self._cli.print_status(
                f"Loading {file_name} config from external file: {path}"
            )

        else:
            self._cli.print_status(f"Loading {file_name} config from default config.")
            path = default_config

        return path

    def parse_config(self, config: dict[str, Any]):
        raise NotImplementedError(
            f"{__class__.__name__}: parse_config has not been implemented"
        )

    def apply_config(self, config: dict[str, Any]):
        raise NotImplementedError(
            f"{__class__.__name__}: apply_config has not been implemented"
        )
