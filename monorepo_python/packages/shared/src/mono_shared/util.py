from .types import User       # relative import within package


def format_user(u: User) -> str:
    return f"{u.id}:{u.name}"


def hello(msg: str) -> str:
    return f"hello, {msg}"
