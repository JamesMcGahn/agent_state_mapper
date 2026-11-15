from dataclasses import dataclass


@dataclass
class AssignmentFilter:
    first_name: str
    last_name: str
    login: str
    filter_name: str
    filter_type: str
    is_public: bool
