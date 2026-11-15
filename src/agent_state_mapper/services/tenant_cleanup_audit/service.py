from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...db import SQLConnectionManager
    from ...models.intra import Tenant
    from .query_worker import TenantCleanupAuditQueryWorker
    from ...cli import CLI

from ...models.intra import Tenant, Node
from ...enums.db_name import DB_NAME


class TenantCleanUpAuditService:
    def __init__(
        self, cli: CLI, db: SQLConnectionManager, worker: TenantCleanupAuditQueryWorker
    ):
        self.cli = cli
        self.db = db
        self.worker = worker

    def clean_up_audit(self, node: Node, tenant: Tenant) -> list[Tenant]:
        self.db.connect(node, DB_NAME.TENANT)
        try:
            user_filters = self.worker.not_inuse_user_filters(self.db, tenant)
            task_filters = self.worker.not_inuse_task_filters(self.db, tenant)
            custom_attributes = self.worker.not_inuse_custom_attributes(self.db, tenant)
            paused_rules = self.worker.paused_rules(self.db, tenant)
            assignment_filters = self.worker.assignment_filters(self.db, tenant)

            print(user_filters)
            print(task_filters)
            print(custom_attributes)
            print(paused_rules)
            print(assignment_filters)

            # TODO - return dc
        finally:
            self.db.disconnect()
