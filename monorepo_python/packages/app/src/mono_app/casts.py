"""Exhaustive Python cast / type-conversion catalogue."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast, Optional

# 1. Builtin constructors (duck-typed "casts").
def builtin_casts() -> None:
    _a: int   = int("42")
    _b: float = float(3)
    _c: str   = str(3.14)
    _d: bool  = bool(1)
    _e: list  = list((1, 2, 3))
    _f: tuple = tuple([1, 2])
    _g: set   = set([1, 2, 2])
    _h: dict  = dict(x=1)
    _i: bytes = bytes("hi", "utf-8")

# 2. Runtime check + narrow via isinstance (type narrowing pattern).
def narrow(x: Any) -> int:
    if isinstance(x, int):
        return x            # Pyright narrows to `int` here
    if isinstance(x, str):
        return int(x)
    return 0

# 3. typing.cast — type-only cast (no runtime effect).
def typed_cast(v: Any) -> int:
    return cast(int, v)     # tells the checker to treat `v` as int

# 4. __int__ / __float__ / __str__ / __bool__ — dunder-driven conversion.
@dataclass
class Celsius:
    value: float
    def __int__(self) -> int:     return int(self.value)
    def __float__(self) -> float: return float(self.value)
    def __str__(self) -> str:     return f"{self.value}°C"
    def __bool__(self) -> bool:   return self.value != 0

# 5. Custom __index__ for "integer-like" objects.
class Port:
    def __init__(self, n: int) -> None: self._n = n
    def __index__(self) -> int: return self._n

# 6. typing.Optional unwrapping.
def unwrap(x: Optional[int]) -> int:
    if x is None:
        raise ValueError("none")
    return x                                # narrowed to int

# 7. Protocol-based structural cast (typing.Protocol).
from typing import Protocol
class Nameable(Protocol):
    name: str

def greet(obj: Nameable) -> str:
    return f"hi, {obj.name}"

def run_casts_demo() -> None:
    builtin_casts()
    print(narrow("42"), narrow(42))
    print(typed_cast("treated as int"))
    c = Celsius(25.5)
    print(int(c), float(c), str(c), bool(c))
    _p: Port = Port(8080)
    print(bytes([_p.__index__() & 0xFF]))
    print(unwrap(1))

    @dataclass
    class P: name: str
    print(greet(P("alice")))
