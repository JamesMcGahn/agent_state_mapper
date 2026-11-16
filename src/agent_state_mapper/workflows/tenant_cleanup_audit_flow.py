from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import CLI

    from ..prompts import Prompts
    from ..app_config import AppConfig
    from ..services.tenant_cleanup_audit import TenantCleanUpAuditService


from ..models.intra import TenantSelection
from ..errors import TenantSelectionError


class TenantCleanUpAuditFlow:

    def __init__(
        self,
        cli: CLI,
        prompts: Prompts,
        config: AppConfig,
        tenant_audit_service: TenantCleanUpAuditService,
        tenant_selection: TenantSelection,
    ):

        self._prompts = prompts
        self._config = config
        self._cli = cli
        self._tenant_audit_service = tenant_audit_service
        self._tenant_selection = tenant_selection

    def run(self) -> None:
        if self._tenant_selection is None:
            raise TenantSelectionError("Select a tenant first.")
        self._tenant_audit_service.clean_up_audit(
            node=self._tenant_selection.node, tenant=self._tenant_selection.tenant
        )
