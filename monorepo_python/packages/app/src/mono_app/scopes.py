# Labeled scope test cases for Python in the monorepo layout.
# See SCOPE_TEST_SPEC.md at repo root. Ported from python/scopes.py,
# with cross-module refs rewritten to target the sibling workspace
# packages `mono_shared` / `mono_utils` and local workspace modules.

# --------------------------------------------------------------------------- S04
module_var = "mod-initial"                            # S04.def — also S05 write target

# --------------------------------------------------------------------------- S09 source
# Aliased import from a sibling workspace package (mono_shared).
from mono_shared import format_user as shared_format_user     # S09.def

# --------------------------------------------------------------------------- S10 source
from .scopes_reexport import re_exported_value         # S10.consumer.import


def s01_local():
    local_a = "S01.local"                              # S01.def
    print(local_a)                                     # S01.read


def s02_closure_read():
    outer_a = "S02.outer"                              # S02.outer.def
    def inner():
        print(outer_a)                                 # S02.inner.read
    inner()


def s03_closure_write():
    counter = 0                                        # S03.outer.def
    def bump():
        nonlocal counter
        counter = counter + 1                          # S03.inner.write
    bump()
    bump()
    return counter                                     # S03.outer.read


def s05_same_module_write():
    global module_var
    module_var = "rotated"                             # S05.write
    print(module_var)                                  # S05.read


def s06_cross_read():
    # Cross-workspace-package READ of a sibling module's constant.
    from mono_shared.types import DEFAULT_ROLE
    return DEFAULT_ROLE                                # S06.read


def s07_cross_write():
    # Cross-workspace-package WRITE via attribute assignment on imported module.
    import mono_shared
    mono_shared.DEFAULT_ROLE = None                    # S07.write — deliberate mutation
    # restore so the rest of the demo works
    from mono_shared.types import Role
    mono_shared.DEFAULT_ROLE = Role.USER


def s08_shadowing():
    module_var = "shadowed"                            # S08.shadow.def
    print(module_var)                                  # S08.shadow.read


def s09_aliased_import():
    # Resolves back to mono_shared.util.format_user through the
    # package's `__all__` re-export plus our `as`.
    from mono_shared.types import User
    print(shared_format_user(User(1, "alice")))        # S09.read


def s10_reexport_chain():
    print(re_exported_value)                           # S10.consumer.read


class Base:
    static_x = 1                                       # S12.static.def / S13.base.def

    def __init__(self, x: int):
        self.x = x                                     # S11.instance.def

    def read_instance(self, x: int):
        # Parameter `x` shadows `self.x` inside this method.
        return x, self.x                               # S11.param.read + S11.instance.read


class Derived(Base):
    def read_inherited(self):
        return self.static_x + 0                       # S13.derived.read


def s14_qualified():
    from . import scopes_ns_pkg
    import importlib
    importlib.import_module("mono_app.scopes_ns_pkg.inner")
    from .scopes_ns_pkg import inner as _inner
    return _inner.Widget("hi")                         # S14.read


def run_scope_demo():
    s01_local()
    s02_closure_read()
    s03_closure_write()
    s05_same_module_write()
    s06_cross_read()
    s07_cross_write()
    s08_shadowing()
    s09_aliased_import()
    s10_reexport_chain()
    b = Base(42)
    print(b.read_instance(100))
    print(Derived(1).read_inherited())
    print(s14_qualified().label)
