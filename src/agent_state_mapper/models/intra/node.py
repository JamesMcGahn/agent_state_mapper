from dataclasses import dataclass, field


@dataclass
class Node:
    name: str
    mt_db: str
    tenant_db: str
    db_server: str
    db_user_name: str = field(repr=False)
    db_password: str = field(repr=False)
    elk_endpoint: str
    elk_api_key: str
