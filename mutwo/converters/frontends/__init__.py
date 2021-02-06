"""Module for routines that convert mutwo objects to external data."""

from mutwo.utilities import tools

from . import abc
from . import csound

# import modules with extra require
for module, dependency in (
    ("midi", "mido"),
    ("reaper", "rpp"),
):
    tools.import_module_if_dependency_has_been_installed(
        "mutwo.converters.frontends.{}".format(module), dependency
    )

del module, dependency, tools
