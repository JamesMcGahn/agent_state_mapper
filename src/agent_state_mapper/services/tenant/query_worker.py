from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dal import TenantDAL
    from ...db import SQLConnectionManager

from ...models.intra import Tenant


class TenantQueryWorker:
    def __init__(self, dal: TenantDAL):
        self.dal = dal

    def run(self, db: SQLConnectionManager) -> list[Tenant]:
        tenants = []
        for name, tenant_id in self.dal.fetch_tenant_rows(db):
            if type(tenant_id) is not int:
                raise ValueError(f"Invalid tenant ID: {tenant_id!r}")
            if not isinstance(name, str) or not name.strip():
                raise ValueError(f"Missing name for tenant {tenant_id}")
            tenants.append(Tenant(tenant_id=tenant_id, name=name))
        return tenants
