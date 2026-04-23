"""Barrel __init__ — canonical way to expose a Python package's public API."""
from .types import User, Role, DEFAULT_ROLE
from .util import format_user, hello

# Explicit public API list — analysers use this to determine what
# `from mono_shared import *` yields.
__all__ = [
    "User",
    "Role",
    "DEFAULT_ROLE",
    "format_user",
    "hello",
]
