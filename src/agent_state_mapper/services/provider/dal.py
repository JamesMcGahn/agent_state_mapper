from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...db import SQLConnectionManager


class ProviderDAL:

    def fetch_acd_providers(
        self, db: SQLConnectionManager, tenant_id: int
    ) -> list[tuple[str, str, str, str]]:

        QUERY = """
        DECLARE @tenant_id INT = ?;

        SELECT DISTINCT 
            ucr.provider_instance_guid, 
            p.ui_display_name, 
            p.name,
            pr.name AS provider_type
        FROM USER_CROSS_REF ucr WITH (nolock)
        JOIN ka_user ku WITH (nolock)
            ON ku.ka_user_guid = ucr.user_id
        JOIN PROVIDER_INSTANCE p WITH (nolock)
            ON p.provider_instance_guid = ucr.provider_instance_guid
        JOIN PROVIDER pr (nolock)
            ON p.provider_guid = pr.provider_guid
        WHERE ku.archived = 0
            AND ucr.tenant_id = @tenant_id
            AND pr.provider_parent_guid = '5988A718-41A5-4154-A7D5-AB742810234C'
        ORDER BY p.ui_display_name
        """
        rows = db.fetch_all(QUERY, (tenant_id,))
        return [(str(row[0]), str(row[1]), str(row[2]), str(row[3])) for row in rows]

    def fetch_intra_call_provider(
        self, db: SQLConnectionManager, tenant_id: int
    ) -> None | tuple[str, str, str, str]:

        QUERY = """
        DECLARE @tenant_id INT = ?;

        SELECT
            p.provider_instance_guid,
            p.ui_display_name,
            p.name,
            pr.name AS provider_type
        FROM PROVIDER_INSTANCE p WITH (NOLOCK)
        JOIN PROVIDER pr WITH (NOLOCK)
            ON p.provider_guid = pr.provider_guid
        WHERE
            p.tenant_id = @tenant_id
            and pr.name = 'id_intra_call'
            
        ORDER BY
            p.ui_display_name;
        """
        row = db.fetch_one(QUERY, (tenant_id,))
        if row is not None:
            return (str(row[0]), str(row[1]), str(row[2]), str(row[3]))
        return None

    def fetch_intra_call_state_config(
        self, db: SQLConnectionManager, tenant_id: int, intra_call_id: str
    ) -> None | str:

        QUERY = """
        DECLARE @tenant_id INT = ?;

        SELECT
            pcv.string_value
        FROM PROVIDER_INSTANCE_CONFIG_VALUE pcv WITH (NOLOCK)
        JOIN PROVIDER_CONFIG_PARAMETER pcp WITH (NOLOCK)
            ON pcv.provider_config_parameter_guid =
            pcp.provider_config_parameter_guid
        WHERE
            pcv.provider_instance_guid =?
            and pcp.name = 'id_intra_call_tenant_state_mapping_key_values'
            and pcv.tenant_id = @tenant_id
        """
        row = db.fetch_one(
            QUERY,
            (
                tenant_id,
                intra_call_id,
            ),
        )
        if row is not None:
            return str(row[0])
        return None
