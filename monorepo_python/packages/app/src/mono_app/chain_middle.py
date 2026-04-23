# T1.middle — hop 1. Re-exports the origin value under the same name.
from .chain_origin import ORIGIN_VALUE     # T1.middle.import

# Deliberate re-export: adding to __all__ makes this module's
# `ORIGIN_VALUE` a first-class exported name.
__all__ = ["ORIGIN_VALUE"]                  # T1.middle.reexport
