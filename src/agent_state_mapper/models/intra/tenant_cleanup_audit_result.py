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
    user_filters: UserFilter
    task_filters: TaskFilter
    custom_attributes: CustomAttribute
    paused_rules: PausedRule
    assignment_filters: AssignmentFilter
