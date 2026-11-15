from dataclasses import dataclass
from .node import Node
from .tenant import Tenant


@dataclass
class TenantSelection:
    tenant: Tenant
    node: Node
