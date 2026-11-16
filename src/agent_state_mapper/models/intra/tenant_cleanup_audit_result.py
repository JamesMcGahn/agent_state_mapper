from dataclasses import dataclass
from .tenant import Tenant
from .user_filter import UserFilter
from .task_filter import TaskFilter
from .custom_attribute import CustomAttribute
from .paused_rule import PausedRule
from .assignment_filter import AssignmentFilter


@dataclass
class TenantCleanupAuditResult:
    tenant: Tenant
    user_filters: list[UserFilter]
    task_filters: list[TaskFilter]
    custom_attributes: list[CustomAttribute]
    paused_rules: list[PausedRule]
    assignment_filters: list[AssignmentFilter]
