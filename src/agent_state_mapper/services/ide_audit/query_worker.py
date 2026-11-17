from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dal import TenantIDEAuditDAL
    from ...db import SQLConnectionManager
    from ...cli import CLI
    from ...models.intra import TenantSelection

from ...models.intra import UserIDEVersion


class TenantIDEAuditQueryWorker:

    def __init__(self, cli: CLI, dal: TenantIDEAuditDAL):
        self.cli = cli
        self.dal = dal

    def user_ide_versions(
        self, db: SQLConnectionManager, tenant_selection: TenantSelection
    ) -> list[UserIDEVersion]:
        user_ide = []
        tenant = tenant_selection.tenant
        node = tenant_selection.node
        for (
            ide_verison,
            user_guid,
            tenant_id,
            tenant_name,
            first_name,
            last_name,
            login,
            event_date,
        ) in self.dal.fetch_user_ide_versions(db, tenant.tenant_id, node.tenant_db):

            try:
                tenant_id = int(tenant_id)
            except ValueError:
                self.cli.print_warn(f"Invalid tenant ID: {tenant_id!r} - Skipping...")
                continue

            user_ide.append(
                UserIDEVersion(
                    ide_verison=ide_verison,
                    user_guid=user_guid,
                    tenant_id=tenant_id,
                    tenant_name=tenant_name,
                    first_name=first_name,
                    last_name=last_name,
                    login=login,
                    event_date=event_date,
                )
            )
        return user_ide
