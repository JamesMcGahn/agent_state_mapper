from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...db import SQLConnectionManager


class TenantDAL:

    def fetch_tenant_rows(self, db: SQLConnectionManager):

        TENANT_QUERY = """
        SELECT name, tenant_id as id
        FROM tenant (NOLOCK)
        WHERE name NOT LIKE 'SYSTEM%' AND name NOT LIKE 'node%' AND in_use = 1
        ORDER BY name
        """
        rows = db.fetch_all(TENANT_QUERY)
        return [(str(row[0]), row[1]) for row in rows]
