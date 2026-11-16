from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...db import SQLConnectionManager
    from ...models.intra import Tenant
    from .query_worker import TenantCleanupAuditQueryWorker
    from ...cli import CLI

from ...models.intra import Tenant, Node, TenantCleanupAuditResult
from ...enums.db_name import DB_NAME


class TenantCleanUpAuditService:
    def __init__(
        self, cli: CLI, db: SQLConnectionManager, worker: TenantCleanupAuditQueryWorker
    ):
        self.cli = cli
        self.db = db
        self.worker = worker

    def clean_up_audit(self, node: Node, tenant: Tenant) -> TenantCleanupAuditResult:
        self.db.connect(node, DB_NAME.MT)
        try:
            self.cli.print_status(
                f"Querying {tenant.name} for Not In Use User Filters."
            )
            user_filters = self.worker.not_inuse_user_filters(self.db, tenant)
            self.cli.print_status(f"Receieved {len(user_filters)} User Filters.")

            self.cli.print_status(
                f"Querying {tenant.name} for Not In Use Task Filters."
            )
            task_filters = self.worker.not_inuse_task_filters(self.db, tenant)
            self.cli.print_status(f"Receieved {len(task_filters)} User Filters.")

            self.cli.print_status(
                f"Querying {tenant.name} for Not In Use Custom Attributes."
            )
            custom_attributes = self.worker.not_inuse_custom_attributes(self.db, tenant)
            self.cli.print_status(f"Receieved {len(task_filters)} Custom Attributes.")

            self.cli.print_status(f"Querying {tenant.name} for Paused Rules.")
            paused_rules = self.worker.paused_rules(self.db, tenant)
            self.cli.print_status(f"Receieved {len(task_filters)} Paused Rules.")

            self.cli.print_status(f"Querying {tenant.name} for Assignment Filters.")
            assignment_filters = self.worker.assignment_filters(self.db, tenant)
            self.cli.print_status(f"Receieved {len(task_filters)} Assignment Filters.")

            return TenantCleanupAuditResult(
                tenant=tenant,
                user_filters=user_filters,
                task_filters=task_filters,
                custom_attributes=custom_attributes,
                paused_rules=paused_rules,
                assignment_filters=assignment_filters,
            )
        finally:
            self.db.disconnect()
