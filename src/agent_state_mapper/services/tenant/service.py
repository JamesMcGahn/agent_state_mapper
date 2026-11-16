from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dal import TenantDAL
    from ...db import SQLConnectionManager
    from ...models.intra import Tenant
    from .query_worker import TenantQueryWorker
    from ...cli import CLI

from ...models.intra import Tenant, Node
from ...enums.db_name import DB_NAME


class TenantService:
    def __init__(self, cli: CLI, db: SQLConnectionManager, worker: TenantQueryWorker):
        self.cli = cli
        self.db = db
        self.worker = worker

    def list_tenants(self, node: Node) -> list[Tenant]:
        self.cli.print_status(f"Getting Tenants for {node.name}")
        self.db.connect(node, DB_NAME.TENANT)
        try:
            return self.worker.run(self.db)
        finally:
            self.db.disconnect()
