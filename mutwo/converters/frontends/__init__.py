"""Convert mutwo objects to external data."""

from mutwo.utilities import tools

from . import csound_constants
from . import csound
from . import ekmelily_constants
from . import ekmelily
from . import isis_constants
from . import isis

# import modules with extra require
for modules, dependencies in (
    (("midi_constants", "midi"), ("mido",)),
    (("reaper",), ("rpp",)),
    (("abjad_attachments", "abjad_constants", "abjad",), ("abjad", "abjadext.nauert")),
):
    for module in modules:
        tools.import_module_if_dependencies_have_been_installed(
            "mutwo.converters.frontends.{}".format(module), dependencies
        )

del module, dependencies, tools
