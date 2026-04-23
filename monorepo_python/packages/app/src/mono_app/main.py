"""Entry point exercising every Python import shape against the
sibling workspace packages `mono-shared` and `mono-utils`."""

# 1. Whole-module import.
import mono_shared
# 2. Submodule import.
import mono_shared.types
# 3. Aliased whole-module.
import mono_utils as u
# 4. `from x import y`.
from mono_shared import format_user, DEFAULT_ROLE
# 5. `from x import y as z`.
from mono_shared.types import User as SharedUser
# 6. Star import — resolves against mono_shared.__all__.
from mono_shared import *    # noqa: F401,F403 — deliberate
# 7. Sibling relative import (inside same package).
from . import helper


def main() -> None:
    user = SharedUser(id=1, name="alice")
    print(format_user(user), DEFAULT_ROLE)

    print("tag:", u.TAG, "clamped:", u.clamp(42, 0, 10))

    # Access via whole-module import.
    print("via module:", mono_shared.types.Role.ADMIN)

    helper.run()

    # Ported coverage from the flat python/ fixture.
    from . import decorators, scopes, imports, advanced, casts
    decorators.run_all_decorator_demos()
    scopes.run_scope_demo()
    _ = imports.exported_function()
    advanced.run_advanced_demo()
    casts.run_casts_demo()

    # Transitive re-export chain: consumer ← chain_deep ← chain_middle ← chain_origin.
    from .chain_deep import VALUE_ALIAS   # T1.consumer.read — must resolve to ORIGIN_VALUE.def
    print(f"transitive: {VALUE_ALIAS}")

    # Cyclic-import sanity: Alpha calls Bravo calls Alpha.
    from . import cycle_a
    print(f"cycle: {cycle_a.kick_off()}")


if __name__ == "__main__":
    main()
