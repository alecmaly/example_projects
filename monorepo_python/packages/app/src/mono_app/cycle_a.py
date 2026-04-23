# C1.a — one half of a cyclic-import pair.
# Type-only cycle: resolved via `if TYPE_CHECKING` so runtime loading
# stays deterministic, but the LSP must still see the B reference.
from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .cycle_b import Bravo                       # C1.a.type_only_import


class Alpha:
    """Alpha defers `Bravo` to method-local import at runtime."""

    def __init__(self, name: str) -> None:
        self.name = name

    def spawn_bravo(self) -> "Bravo":
        # Deferred runtime import — the classic cycle-break pattern.
        from .cycle_b import Bravo                   # C1.a.runtime_import
        return Bravo(self.name + "/b")

    def describe(self) -> str:
        return f"Alpha({self.name})"


def kick_off() -> str:
    a = Alpha("root")
    b = a.spawn_bravo()
    return b.bounce_to_alpha()                       # calls back into Alpha
