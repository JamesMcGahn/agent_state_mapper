from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dal import TenantCleanupAuditDAL
    from ...db import SQLConnectionManager
    from ...cli import CLI

from ...models.intra import (
    Tenant,
    UserFilter,
    TaskFilter,
    CustomAttribute,
    PausedRule,
    AssignmentFilter,
)


class TenantCleanupAuditQueryWorker:

    def __init__(self, cli: CLI, dal: TenantCleanupAuditDAL):
        self.cli = cli
        self.dal = dal

    def not_inuse_user_filters(
        self, db: SQLConnectionManager, tenant: Tenant
    ) -> list[UserFilter]:
        user_filters = []
        for name in self.dal.fetch_not_inuse_user_filters(db, tenant.tenant_id):
            user_filters.append(UserFilter(name=name))
        return user_filters

    def not_inuse_task_filters(
        self, db: SQLConnectionManager, tenant: Tenant
    ) -> list[TaskFilter]:
        task_filters = []
        for name in self.dal.fetch_not_inuse_task_filters(db, tenant.tenant_id):
            task_filters.append(TaskFilter(name=name))
        return task_filters

    def not_inuse_custom_attributes(
        self, db: SQLConnectionManager, tenant: Tenant
    ) -> list[CustomAttribute]:
        attributes = []
        for name in self.dal.fetch_not_inuse_custom_attributes(db, tenant.tenant_id):
            attributes.append(CustomAttribute(name=name))
        return attributes

    def paused_rules(
        self, db: SQLConnectionManager, tenant: Tenant
    ) -> list[PausedRule]:
        attributes = []
        for name, time in self.dal.fetch_paused_rules(db, tenant.tenant_id):

            attributes.append(PausedRule(name=name, paused_date=time))
        return attributes

    def assignment_filters(
        self, db: SQLConnectionManager, tenant: Tenant
    ) -> list[AssignmentFilter]:
        assignment_filters = []
        for (
            first_name,
            last_name,
            login,
            filter_name,
            filter_type,
            public_private,
        ) in self.dal.fetch_assigment_filters(db, tenant.tenant_id):

            assignment_filters.append(
                AssignmentFilter(
                    first_name=first_name,
                    last_name=last_name,
                    login=login,
                    filter_name=filter_name,
                    filter_type=filter_type,
                    is_public=public_private == "public",
                )
            )
        return assignment_filters
