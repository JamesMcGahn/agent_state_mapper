from typing import Any, ClassVar, Protocol
from dataclasses import Field


class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]
