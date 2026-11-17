from dataclasses import dataclass


@dataclass
class UserIDEVersion:
    ide_verison: str
    user_guid: str
    tenant_id: int
    tenant_name: str
    first_name: str
    last_name: str
    login: str
