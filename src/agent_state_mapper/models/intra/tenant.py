from dataclasses import dataclass, field


@dataclass
class Tenant:
    tenant_id: int
    name: str
