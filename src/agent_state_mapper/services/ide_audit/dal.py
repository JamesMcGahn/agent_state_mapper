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

        WITH LatestLogins AS (
            SELECT
                ueh.param_value4 AS ide_version,
                ueh.ka_user_guid,
                ueh.tenant_id,
                ueh.processed_date,
                ROW_NUMBER() OVER (
                    PARTITION BY ueh.ka_user_guid
                    ORDER BY ueh.processed_date DESC
                ) AS rn
            FROM USER_EVENT_HIST ueh
            WHERE
                ueh.tenant_id = @tenant_id
                AND ueh.processed_date >= @start_date
                AND ueh.param_value5 = 'loggedin'
                AND ueh.param_value4 IS NOT NULL
                AND ueh.param_value4 <> '0.0.0.0'
        )
        SELECT
            ll.ide_version,
            ll.ka_user_guid,
            ll.tenant_id,
            t.name AS tenant_name,
            ku.first_name,
            ku.last_name,
            ku.login,
            ll.processed_date
        FROM LatestLogins ll
        INNER JOIN {quoted_db}..TENANT t
            ON t.tenant_id = ll.tenant_id
        INNER JOIN ka_user ku
            ON ku.ka_user_guid = ll.ka_user_guid
        WHERE ll.rn = 1
        ORDER BY ll.ide_version, ll.ka_user_guid;
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
                row[7],
            )
            for row in rows
        ]
