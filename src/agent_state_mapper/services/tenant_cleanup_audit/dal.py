from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...db import SQLConnectionManager


class TenantCleanupAuditDAL:

    def fetch_not_inuse_user_filters(self, db: SQLConnectionManager, tenant_id: int):

        QUERY = """
        SET NOCOUNT ON

        SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED

        DECLARE @tenant_id INT = ?;

        SELECT obf.name
        FROM OBJECT_FILTER obf
        LEFT JOIN UI_PARAM_VALUE upv
            ON TRY_CONVERT(uniqueidentifier, CONVERT(varchar(36), upv.value))
            = obf.object_filter_guid
        WHERE obf.tenant_id = @tenant_id
            AND upv.value IS NULL
            AND obf.object_filter_result_type_id = 0
            AND obf.object_filter_access_type_id = 0

        INTERSECT

        SELECT obf.name
        FROM OBJECT_FILTER obf
        LEFT JOIN UI_PARAM_FIELD_VALUE upv
            ON TRY_CONVERT(uniqueidentifier, CONVERT(varchar(36), upv.value))
            = obf.object_filter_guid
        WHERE obf.tenant_id = @tenant_id
            AND upv.value IS NULL
            AND obf.object_filter_result_type_id = 0
            AND obf.object_filter_access_type_id = 0

        INTERSECT

        SELECT obf.name
        FROM OBJECT_FILTER obf
        LEFT JOIN ASSIGNMENT_DEFINITION ad
            ON ad.user_filter_guid = obf.object_filter_guid
        WHERE obf.tenant_id = @tenant_id
            AND obf.object_filter_result_type_id = 0
            AND obf.object_filter_access_type_id = 0
            AND ad.assignment_definition_guid IS NULL

        INTERSECT

        SELECT obf.name
        FROM OBJECT_FILTER obf
        LEFT JOIN PERMISSION p
            ON p.user_view_guid = obf.object_filter_guid
        WHERE obf.tenant_id = @tenant_id
            AND obf.object_filter_result_type_id = 0
            AND obf.object_filter_access_type_id = 0
            AND p.user_view_guid IS NULL;
        """
        rows = db.fetch_all(QUERY, (tenant_id,))
        return [(str(row[0])) for row in rows]

    def fetch_not_inuse_task_filters(self, db: SQLConnectionManager, tenant_id: int):
        QUERY = """
            SET NOCOUNT ON

            SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED

            DECLARE @tenant_id INT = ?;
            SELECT obf.name
            FROM OBJECT_FILTER AS obf
            LEFT JOIN UI_PARAM_VALUE AS upv
                ON LEN(upv.value) = 36
            AND TRY_CONVERT(uniqueidentifier, CONVERT(varchar(36), upv.value))
                = obf.object_filter_guid
            WHERE obf.tenant_id = @tenant_id
            AND obf.object_filter_result_type_id = 1
            AND upv.value IS NULL

            INTERSECT

            SELECT obf.name
            FROM OBJECT_FILTER AS obf
            LEFT JOIN UI_PARAM_FIELD_VALUE AS upv
                ON LEN(upv.value) = 36
            AND TRY_CONVERT(uniqueidentifier, CONVERT(varchar(36), upv.value))
                = obf.object_filter_guid
            WHERE obf.tenant_id = @tenant_id
            AND obf.object_filter_result_type_id = 1
            AND upv.value IS NULL

            INTERSECT

            SELECT obf.name
            FROM OBJECT_FILTER AS obf
            LEFT JOIN ASSIGNMENT_DEFINITION AS ad
                ON ad.task_filter_guid = obf.object_filter_guid
            WHERE obf.tenant_id = @tenant_id
            AND obf.object_filter_result_type_id = 1
            AND ad.assignment_definition_guid IS NULL

            INTERSECT

            SELECT obf.name
            FROM OBJECT_FILTER AS obf
            LEFT JOIN PERMISSION AS p
                ON p.task_view_guid = obf.object_filter_guid
            WHERE obf.tenant_id = @tenant_id
            AND obf.object_filter_result_type_id = 1
            AND p.task_view_guid IS NULL;

        """
        rows = db.fetch_all(QUERY, (tenant_id,))
        return [(str(row[0])) for row in rows]

    def fetch_not_inuse_custom_attributes(
        self, db: SQLConnectionManager, tenant_id: int
    ):
        QUERY = """
            SET NOCOUNT ON

            SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED

            DECLARE @tenant_id INT = ?;


            -- identify attributes not used by user
            SELECT 
                DISTINCT
                CASE 
                WHEN data_type = 1
                THEN cg.name 
                ELSE
                ca.name
                END AS attribute_name
            FROM 
                CUSTOM_ATTRIBUTE ca
            INNER JOIN CUSTOM_ATTRIBUTE_GROUP cg 
                ON cg.custom_attribute_group_guid = ca.custom_attribute_group_guid AND cg.tenant_id = ca.tenant_id
            LEFT JOIN (
            SELECT
                tmpca.custom_attribute_guid, 
                tmpca.custom_attribute_group_guid  
            FROM 
                KA_USER_CUSTOM_ATTRIBUTE tmpkca
            INNER JOIN CUSTOM_ATTRIBUTE tmpca ON tmpca.custom_attribute_guid = tmpkca.custom_attribute_guid AND tmpkca.tenant_id = tmpca.tenant_id
            WHERE tmpkca.tenant_id = @tenant_id
            ) tca
            ON 
                (
                    (ca.data_type = 1 AND tca.custom_attribute_group_guid = cg.custom_attribute_group_guid)
                        OR 
                    (ca.data_type <> 1 AND tca.custom_attribute_guid = ca.custom_attribute_guid)
                )
            WHERE ca.tenant_id = @tenant_id AND tca.custom_attribute_guid IS NULL

            INTERSECT

            -- identify attributes not used by task
            SELECT 
                DISTINCT
                CASE 
                WHEN data_type = 1
                THEN cg.name 
                ELSE
                ca.name
                END AS attribute_name
            FROM 
                CUSTOM_ATTRIBUTE ca
            INNER JOIN CUSTOM_ATTRIBUTE_GROUP cg 
                ON cg.custom_attribute_group_guid = ca.custom_attribute_group_guid AND cg.tenant_id = ca.tenant_id
            LEFT JOIN (
            SELECT
                tmpca.custom_attribute_guid, 
                tmpca.custom_attribute_group_guid  
            FROM 
                TASK_CUSTOM_ATTRIBUTE tmptca
            INNER JOIN CUSTOM_ATTRIBUTE tmpca ON tmpca.custom_attribute_guid = tmptca.custom_attribute_guid AND tmptca.tenant_id = tmpca.tenant_id
            WHERE tmptca.tenant_id = @tenant_id
            ) tca
            ON 
                (
                    (ca.data_type = 1 AND tca.custom_attribute_group_guid = cg.custom_attribute_group_guid)
                        OR 
                    (ca.data_type <> 1 AND tca.custom_attribute_guid = ca.custom_attribute_guid)
                )
            WHERE ca.tenant_id = @tenant_id AND tca.custom_attribute_guid IS NULL

            INTERSECT

            -- identify attributes not used by assignment group

            SELECT 
                DISTINCT
                CASE 
                WHEN data_type = 1
                THEN cg.name 
                ELSE
                ca.name
                END AS attribute_name
            FROM 
                CUSTOM_ATTRIBUTE ca
            INNER JOIN CUSTOM_ATTRIBUTE_GROUP cg 
                ON cg.custom_attribute_group_guid = ca.custom_attribute_group_guid AND cg.tenant_id = ca.tenant_id
            LEFT JOIN (
            SELECT
                tmpca.custom_attribute_guid, 
                tmpca.custom_attribute_group_guid  
            FROM 
                ASSIGNMENT_DEFINITION_CUSTOM_ATTRIBUTE tmpadca
            INNER JOIN CUSTOM_ATTRIBUTE tmpca ON tmpca.custom_attribute_guid = tmpadca.custom_attribute_guid AND tmpadca.tenant_id = tmpca.tenant_id
            WHERE tmpadca.tenant_id = @tenant_id
            ) tca
            ON 
                (
                    (ca.data_type = 1 AND tca.custom_attribute_group_guid = cg.custom_attribute_group_guid)
                        OR 
                    (ca.data_type <> 1 AND tca.custom_attribute_guid = ca.custom_attribute_guid)
                )
            WHERE ca.tenant_id = @tenant_id AND tca.custom_attribute_guid IS NULL

            INTERSECT

            -- identify attributes not used by assignment 

            SELECT 
                DISTINCT
                CASE 
                    WHEN data_type = 1
                    THEN cg.name 
                    ELSE
                    ca.name
                END AS attribute_name
            FROM 
                CUSTOM_ATTRIBUTE ca
            INNER JOIN CUSTOM_ATTRIBUTE_GROUP cg 
                ON cg.custom_attribute_group_guid = ca.custom_attribute_group_guid AND cg.tenant_id = ca.tenant_id
            LEFT JOIN (
            SELECT
                tmpca.custom_attribute_guid, 
                tmpca.custom_attribute_group_guid  
            FROM 
                ASSIGNMENT_INSTANCE_CUSTOM_ATTRIBUTE tmpaica
            INNER JOIN CUSTOM_ATTRIBUTE tmpca ON tmpca.custom_attribute_guid = tmpaica.custom_attribute_guid AND tmpaica.tenant_id = tmpca.tenant_id
            WHERE tmpaica.tenant_id = @tenant_id
            ) tca
            ON 
                (
                    (ca.data_type = 1 AND tca.custom_attribute_group_guid = cg.custom_attribute_group_guid)
                        OR 
                    (ca.data_type <> 1 AND tca.custom_attribute_guid = ca.custom_attribute_guid)
                )
            WHERE ca.tenant_id = @tenant_id AND tca.custom_attribute_guid IS NULL

            INTERSECT

            -- identify attributes not used by rule

            SELECT DISTINCT
                CASE 
                    WHEN ca.data_type = 1 
                    THEN cg.name  
                    ELSE ca.name                        
                END AS attribute_name
            FROM 
                CUSTOM_ATTRIBUTE ca
            INNER JOIN CUSTOM_ATTRIBUTE_GROUP cg 
                ON cg.custom_attribute_group_guid = ca.custom_attribute_group_guid AND cg.tenant_id = ca.tenant_id
            LEFT JOIN (
                SELECT DISTINCT tenant_id, LOWER(TRIM(value)) AS field_value
                FROM RULE_ACTION_INSTANCE_PARAMETER_MAPPING 
                CROSS APPLY STRING_SPLIT(field_value, '|')
                WHERE tenant_id = @tenant_id
            ) sv 
                ON 
                (
                    (ca.data_type = 1 AND sv.field_value = CAST(cg.custom_attribute_group_guid AS NVARCHAR(36))) 
                    OR 
                    (ca.data_type <> 1 AND sv.field_value = CAST(ca.custom_attribute_guid AS NVARCHAR(36))) 
                )
                AND ca.tenant_id = sv.tenant_id
            WHERE 
            ca.tenant_id = @tenant_id 
                AND 
            sv.field_value IS NULL  
        """
        rows = db.fetch_all(QUERY, (tenant_id,))
        return [(str(row[0])) for row in rows]

    def fetch_paused_rules(self, db: SQLConnectionManager, tenant_id: int):
        QUERY = """
            DECLARE @tenant_id INT = ?;

            select name, pause_date_time from UI_RULE with(Nolock)
            -- REMOVED from the select:  rule_guid, tenant_id, rule_type_id, rule_parsed_condition, rule_status_type_id, is_paused, user_criteria, created_by, created_date, modified_by, modified_date from UI_RULE with(Nolock)
            --select * from UI_RULE with(Nolock)
            where is_paused =1 and pause_date_time <= DATEADD(DAY, -30, GETDATE())
            and tenant_id = @tenant_id;
        """
        rows = db.fetch_all(QUERY, (tenant_id,))
        return [(str(row[0]), row[1]) for row in rows]

    def fetch_assigment_filters(self, db: SQLConnectionManager, tenant_id: int):
        QUERY = """
            SET NOCOUNT ON
            SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED
            DECLARE @tenant_id INT = ?;

            SELECT ka.first_name, ka.last_name, ka.login, filter.name as FilterName, ofrt.name as FilterType,case 
            when filter.object_filter_access_type_id = '1' then 'private' 
            else 'public'
            End as PublicOrPrivate
            FROM OBJECT_FILTER filter
            LEFT JOIN KA_USER ka on ka.ka_user_guid = filter.private_filter_owner_ka_user_guid
            LEFT JOIN OBJECT_FILTER_RESULT_TYPE ofrt on ofrt.object_filter_result_type_id = filter.object_filter_result_type_id
            where filter.object_filter_result_type_id in ('3','4','8') 
            and filter.tenant_id = @tenant_id
            AND filter.object_filter_access_type_id in ('1','0')
        """
        rows = db.fetch_all(QUERY, (tenant_id,))
        return [
            (
                str(row[0]),
                str(row[1]),
                str(row[2]),
                str(row[3]),
                str(row[4]),
                str(row[5]),
            )
            for row in rows
        ]
