# T1.deep — hop 2. Pulls from middle and renames on re-export.
from .chain_middle import ORIGIN_VALUE as VALUE_ALIAS   # T1.deep.import (aliased)

__all__ = ["VALUE_ALIAS"]                                # T1.deep.reexport
