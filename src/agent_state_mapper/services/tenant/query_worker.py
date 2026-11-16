from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dal import TenantDAL
    from ...db import SQLConnectionManager
    from ...cli import CLI

from ...models.intra import Tenant
from ...errors import TenantSelectionError


class TenantQueryWorker:
    def __init__(self, cli: CLI, dal: TenantDAL):
        self.cli = cli
        self.dal = dal

    def run(self, db: SQLConnectionManager) -> list[Tenant]:
        tenants = []
        for name, tenant_id in self.dal.fetch_tenant_rows(db):
            if type(tenant_id) not in (int, str):
                self.cli.print_warn(f"Invalid tenant ID: {tenant_id!r} - Skipping...")
                continue
            if not isinstance(name, str) or not name.strip():
                self.cli.print_warn(
                    f"Missing name for tenant {tenant_id} - Skipping..."
                )
                continue
            try:
                tenant_id = int(tenant_id)
            except ValueError:
                self.cli.print_warn(f"Invalid tenant ID: {tenant_id!r} - Skipping...")
                continue

            tenants.append(Tenant(tenant_id=tenant_id, name=name))
        self.cli.print_status(f"Received {len(tenants)}...")
        if not tenants:
            message = "Received 0 tenants for node."
            self.cli.print_error(message)
            raise TenantSelectionError(message)
        return tenants
