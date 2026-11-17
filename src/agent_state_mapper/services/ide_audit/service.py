from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...db import SQLConnectionManager
    from ...models.intra import TenantSelection
    from .query_worker import TenantIDEAuditQueryWorker
    from ...cli import CLI

from ...models.intra import TenantIDEAuditResult
from ...enums.db_name import DB_NAME


class TenantIDEAuditService:

    def __init__(
        self, cli: CLI, db: SQLConnectionManager, worker: TenantIDEAuditQueryWorker
    ):
        self.cli = cli
        self.db = db
        self.worker = worker

    def clean_up_audit(self, tenant_selection: TenantSelection) -> TenantIDEAuditResult:
        tenant = tenant_selection.tenant
        node = tenant_selection.node
        self.db.connect(node, DB_NAME.MT)
        try:
            self.cli.print_status(
                f"Querying {tenant.name} for User's IDE Versions for the last 30 days."
            )
            user_ide_versions = self.worker.user_ide_versions(self.db, tenant_selection)
            self.cli.print_status(f"Receieved {len(user_ide_versions)} User Records.")

            return TenantIDEAuditResult(tenant=tenant, users_ide=user_ide_versions)
        finally:
            self.db.disconnect()
