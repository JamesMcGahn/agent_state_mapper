from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import CLI

    from ..prompts import Prompts
    from ..app_config import AppConfig
    from ..services.tenant import TenantService


from ..errors.network import NotAuthenticatedException


class TenantSelectionFlow:

    def __init__(
        self,
        cli: CLI,
        prompts: Prompts,
        config: AppConfig,
        tenant_service: TenantService,
    ):

        self._prompts = prompts
        self._config = config
        self._cli = cli
        self._tenant_service = tenant_service

    def run(self) -> None:

        while True:
            try:
                node_list = self._config.node_list
                print(node_list)
                node = self._prompts.prompt_user_for_node_selection(node_list)
                tenants = self._tenant_service.list_tenants(node)

                return

            except NotAuthenticatedException:
                self._cli.print_error(
                    "Authentication failed. Check your client ID, client secret, and region. Try again."
                )
