from dataclasses import dataclass
from .tenant import Tenant
from .user_ide_version import UserIDEVersion


@dataclass
class TenantIDEAuditResult:
    tenant: Tenant
    users_ide: list[UserIDEVersion]
