# C1.b — other half of the cycle. Closes the loop back to Alpha.
from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .cycle_a import Alpha


class Bravo:
    def __init__(self, tag: str) -> None:
        self.tag = tag

    def bounce_to_alpha(self) -> str:
        from .cycle_a import Alpha                  # C1.b.runtime_import (deferred)
        return Alpha(f"bounce-from-{self.tag}").describe()
