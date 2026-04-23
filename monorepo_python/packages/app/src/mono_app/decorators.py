"""Comprehensive Python decorator coverage — ported from python/decorators.py.

Exercises every common decorator shape so the LSP's symbol / callable /
var-ref extraction has to handle each kind. Self-contained — no
workspace deps beyond stdlib.
"""
from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol, TypeVar
from abc import abstractmethod

T = TypeVar("T")

# 1. Plain function decorator (stateless)
def trace(fn: Callable[..., T]) -> Callable[..., T]:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs) -> T:
        print(f"-> {fn.__name__}({args}, {kwargs})")
        out = fn(*args, **kwargs)
        print(f"<- {fn.__name__}")
        return out
    return wrapper


# 2. Parameterised decorator
def retry(times: int = 3, exceptions: tuple = (Exception,)):
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*a, **kw):
            last: BaseException | None = None
            for _ in range(times):
                try:
                    return fn(*a, **kw)
                except exceptions as e:
                    last = e
            assert last is not None
            raise last
        return wrapper
    return deco


# 3. Class-based decorator
class CallCounter:
    def __init__(self, fn):
        self.fn = fn
        self.count = 0
        functools.update_wrapper(self, fn)
    def __call__(self, *a, **kw):
        self.count += 1
        return self.fn(*a, **kw)


# 4. Decorator chain
@trace
@retry(times=2)
@CallCounter
def flaky(x: int) -> int:
    if x < 0:
        raise ValueError("bad")
    return x * 2


# 5. @property / @.setter / @.deleter triplet
class Temperature:
    def __init__(self, celsius: float = 0.0):
        self._c = celsius

    @property
    def celsius(self) -> float:
        return self._c

    @celsius.setter
    def celsius(self, v: float) -> None:
        if v < -273.15:
            raise ValueError("below absolute zero")
        self._c = v

    @celsius.deleter
    def celsius(self) -> None:
        self._c = 0.0

    @property
    def fahrenheit(self) -> float:
        return self._c * 9 / 5 + 32


# 6. @classmethod / @staticmethod
class Account:
    _next_id = 1

    def __init__(self, name: str, owner_id: int):
        self.name = name
        self.owner_id = owner_id

    @classmethod
    def create(cls, name: str) -> "Account":
        inst = cls(name, cls._next_id)
        cls._next_id += 1
        return inst

    @staticmethod
    def normalise(name: str) -> str:
        return name.strip().lower()


# 7. @dataclass (frozen + slots variant)
@dataclass
class Point:
    x: float
    y: float
    label: str = "p"
    tags: list[str] = field(default_factory=list)

@dataclass(frozen=True, slots=True)
class FrozenPoint:
    x: float
    y: float


# 8. @abstractmethod stacked on @classmethod
from abc import ABC

class Storage(ABC):
    @classmethod
    @abstractmethod
    def connect(cls, uri: str) -> "Storage": ...

    @abstractmethod
    def put(self, key: str, value: bytes) -> None: ...


class MemoryStorage(Storage):
    def __init__(self) -> None:
        self._m: dict[str, bytes] = {}

    @classmethod
    def connect(cls, uri: str) -> "MemoryStorage":
        return cls()

    def put(self, key: str, value: bytes) -> None:
        self._m[key] = value


# 9. typing.Protocol — structural typing
class Drawable(Protocol):
    def draw(self) -> None: ...


class Square:
    def __init__(self, side: float) -> None:
        self.side = side
    def draw(self) -> None:
        print(f"[square side={self.side}]")


def render(d: Drawable) -> None:
    d.draw()


# 10. Class decorator
def final_fields(cls: type) -> type:
    original_setattr = cls.__setattr__
    allowed = set(cls.__annotations__.keys())

    def __setattr__(self, name: str, value: Any) -> None:
        if name not in allowed:
            raise AttributeError(f"unknown attribute {name!r}")
        original_setattr(self, name, value)

    cls.__setattr__ = __setattr__  # type: ignore[assignment]
    return cls


@final_fields
class Config:
    host: str
    port: int


# 11. functools.singledispatch
@functools.singledispatch
def describe(obj) -> str:
    return f"object of type {type(obj).__name__}"

@describe.register
def _(obj: int) -> str:
    return f"int: {obj}"

@describe.register
def _(obj: str) -> str:
    return f"str of length {len(obj)}"


def run_all_decorator_demos() -> None:
    print("flaky:", flaky(3))
    print("flaky.count:", flaky.count)

    t = Temperature(25)
    t.celsius = 30
    del t.celsius
    print("after delete, celsius:", t.celsius, "F:", t.fahrenheit)

    a = Account.create(Account.normalise("  ALICE  "))
    print(a.name, a.owner_id)

    p = Point(1, 2, tags=["a"])
    fp = FrozenPoint(0, 0)
    print(p, fp)

    s: Storage = MemoryStorage.connect("mem://")
    s.put("k", b"v")

    render(Square(3.0))

    c = Config()
    c.host = "localhost"
    c.port = 8080

    print(describe(42), "/", describe("hi"), "/", describe(3.14))
