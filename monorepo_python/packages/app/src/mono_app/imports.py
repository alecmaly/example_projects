# Exhaustive catalogue of Python import/export forms — monorepo edition.
# Same coverage as python/imports.py but biased toward workspace-package
# imports.

# 1. whole-module import
import mono_shared
# 2. submodule import
import mono_shared.types
# 3. aliased whole-module
import mono_shared.types as shared_types
# 4. from ... import X
from mono_shared import format_user
# 5. from ... import X, Y, Z
from mono_shared.types import User, Role, DEFAULT_ROLE
# 6. from ... import X as Y
from mono_shared import hello as greet
# 7. star import (resolves against mono_shared.__all__)
from mono_shared import *               # noqa: F401,F403
# 8. relative import within this package
from . import helper
# 9. conditional import
try:
    import mono_utils as _u
except ImportError:
    _u = None   # type: ignore
# 10. runtime import via importlib
import importlib
_utils_mod = importlib.import_module("mono_utils")
# 11. TYPE_CHECKING-gated
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mono_shared.types import User as _UserType  # noqa: F401

# --- exports ---
PUBLIC = 1
_PRIVATE = 2
__all__ = ["PUBLIC", "exported_function"]

def exported_function() -> int:
    u = User(id=1, name="alice")
    return (
        len(format_user(u))
        + len(greet("x"))
        + shared_types.DEFAULT_ROLE.value.__len__()
        + (_u.TAG.__len__() if _u else 0)
        + _utils_mod.clamp(1, 0, 10)
        + len(helper.__name__)
        + mono_shared.Util.__class__.__name__.__len__() if False else 0
    )
