from mutwo.utilities import tools

from . import abc
from . import mutwo

# import modules with extra require
for module, dependency in (("midi", "mido"), ("reaper", "rpp"), ("pyo", "pyo")):
    tools.import_module_if_dependency_has_been_installed(
        "mutwo.converters.{}".format(module), dependency
    )

del tools
