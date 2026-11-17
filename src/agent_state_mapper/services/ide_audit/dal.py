from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...db import SQLConnectionManager
import re


class TenantIDEAuditDAL:

    def fetch_user_ide_versions(
        self,
        db: SQLConnectionManager,
        tenant_id: int,
        tenant_db: str,
        query_period: int = 30,
    ):
        if not isinstance(tenant_db, str) or not re.fullmatch(
            r"[A-Za-z0-9_-]{1,128}", tenant_db
        ):
            raise ValueError("Invalid database name.")

        quoted_db = f"[{tenant_db}]"
        # trunk-ignore(bandit/B608)
        QUERY = f"""
        SET NOCOUNT ON;
        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

        DECLARE @tenant_id INT = ?;
        DECLARE @start_date DATETIME = DATEADD(DAY, -?, GETDATE());

        SELECT DISTINCT
            ueh.param_value4 AS ide_version,
            ueh.ka_user_guid,
            ueh.tenant_id,
            t.name AS tenant_name,
            ku.first_name,
            ku.last_name,
            ku.login
        FROM USER_EVENT_HIST ueh
        INNER JOIN {quoted_db}..TENANT t
            ON t.tenant_id = ueh.tenant_id
        INNER JOIN ka_user ku
            ON ku.ka_user_guid = ueh.ka_user_guid
        WHERE
            ueh.tenant_id = @tenant_id
            AND ueh.processed_date >= @start_date
            AND ueh.param_value5 = 'loggedin'
            AND ueh.param_value4 IS NOT NULL
            AND ueh.param_value4 <> '0.0.0.0'
        ORDER BY
            ide_version,
            ueh.ka_user_guid;
        """
        rows = db.fetch_all(
            QUERY,
            (
                tenant_id,
                query_period,
            ),
        )
        return [
            (
                str(row[0]),
                str(row[1]),
                row[2],
                str(row[3]),
                str(row[4]),
                str(row[5]),
                str(row[6]),
            )
            for row in rows
        ]
