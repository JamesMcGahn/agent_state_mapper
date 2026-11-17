from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..cli import CLI
    from ..services.ide_audit import TenantIDEAuditService, TenantIDEAuditSheetService


from ..models.intra import TenantSelection
from ..errors import TenantSelectionError


class TenantIDEAuditFlow:

    def __init__(
        self,
        cli: CLI,
        tenant_ide_audit_service: TenantIDEAuditService,
        tenant_selection: TenantSelection,
        reports: TenantIDEAuditSheetService,
    ):
        self._cli = cli
        self._tenant_ide_audit_service = tenant_ide_audit_service
        self._tenant_selection = tenant_selection
        self._reports = reports

    def run(self) -> None:
        if self._tenant_selection is None:
            raise TenantSelectionError("Select a tenant first.")
        audit_result = self._tenant_ide_audit_service.clean_up_audit(
            tenant_selection=self._tenant_selection
        )
        compare_output = self._reports.get_output_path(
            file_name=f"{self._tenant_selection.tenant.name}_ide_versions",
            tenant=self._tenant_selection.tenant,
        )
        self._reports.write_analyze(
            audit_result=audit_result, output_path=compare_output
        )
