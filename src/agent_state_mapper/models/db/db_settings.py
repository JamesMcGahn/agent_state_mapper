from dataclasses import dataclass, field


@dataclass(frozen=True)
class DBSettings:
    server: str
    database: str
    username: str = field(repr=False)
    password: str = field(repr=False)
