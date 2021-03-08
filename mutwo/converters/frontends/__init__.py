"""Convert mutwo objects to external data."""

from mutwo.utilities import tools

from . import csound_constants
from . import csound
# from . import isis

# import modules with extra require
for modules, dependency in (
    (("midi_constants", "midi"), "mido"),
    (("reaper",), "rpp"),
):
    for module in modules:
        tools.import_module_if_dependency_has_been_installed(
            "mutwo.converters.frontends.{}".format(module), dependency
        )

del module, dependency, tools
