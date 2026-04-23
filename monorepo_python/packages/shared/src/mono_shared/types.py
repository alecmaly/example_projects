from dataclasses import dataclass
from enum import Enum


@dataclass
class User:
    id: int
    name: str


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


DEFAULT_ROLE = Role.USER
