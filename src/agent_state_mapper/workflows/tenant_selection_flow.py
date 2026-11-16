from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import CLI

    from ..prompts import Prompts
    from ..app_config import AppConfig
    from ..services.tenant import TenantService


from ..models.intra import TenantSelection
from ..errors import TenantSelectionError


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

    def run(self) -> TenantSelection:
        while True:
            node_list = self._config.node_list
            node = self._prompts.prompt_user_for_node_selection(node_list)
            if not node:
                msg = "Node was not selected"
                self._cli.print_error(msg)
                raise TenantSelectionError(msg)

            tenants = self._tenant_service.list_tenants(node)

            if not tenants:
                msg = "Database did not return any tenants."
                self._cli.print_error(msg)
                raise TenantSelectionError(msg)

            tenant = self._prompts.prompt_user_for_tenant_selection(tenants)
            return TenantSelection(tenant=tenant, node=node)
