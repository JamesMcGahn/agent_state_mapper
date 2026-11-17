from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserIDEVersion:
    ide_verison: str
    user_guid: str
    tenant_id: int
    tenant_name: str
    first_name: str
    last_name: str
    login: str
    event_date: datetime
