"""
Presentation
************
This package contains MatMat constants.

These constants are used throughout the whole model as references, especially
to avoid string duplications.
Any change to these constants shall be properly analyzed in advance.

All constants are re-exported for retro-compatibility
"""


def _check_uniqueness(*modules):
    """
    Check that no constant name is defined in more than one of the given modules.

    Iterates over all public names (not starting with ``_``) exposed by each
    module and raises an :exc:`ImportError` listing every name that appears in
    more than one module.

    Parameters:
        *modules (types.ModuleType):
            Modules to inspect

    Raises:
        ImportError : If one or more names are defined in multiple modules
    """
    seen = {}
    conflicts = []
    for module in modules:
        for name in dir(module):
            if name.startswith("_"):
                continue
            if name in seen:
                conflicts.append(
                    f"{name}: {seen[name].__name__} vs {module.__name__}"
                )
            else:
                seen[name] = module
    if conflicts:
        raise ImportError("Duplicated constants:\n" + "\n".join(conflicts))


from . import core, domain, index, io, version

_check_uniqueness(core, domain, index, io, version)

from .core import *
from .domain import *
from .index import *
from .io import *
from .version import *
