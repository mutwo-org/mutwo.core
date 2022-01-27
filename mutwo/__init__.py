"""Mutwo is an event based framework for composing music or other time-based arts.

The structure of the framework is centred around objects with a :attr:`duration`
property which are called **Events** (and which are defined in the :mod:`mutwo.events`
package). These events may have several more attributes besides their duration
attribute (e. g. pitch, volume). Abstractions for such attributes are defined in
:mod:`mutwo.parameters`. The :mod:`mutwo.converters` package aims to translate
mutwo data to third-party software data (or upside down). The :mod:`mutwo.generators`
package supports algorithmic generation of artistic data.
"""

from importlib.metadata import entry_points
import sys
import warnings

try:
    discovered_plugin_list = entry_points()["mutwo"]
except KeyError:
    warnings.warn(
        "No mutwo plugin could be found. "
        "Without plugins mutwo is only an empty namespace. "
        "Please read the mutwo README.md at "
        "'https://github.com/mutwo-org/mutwo' for further information."
    )
    discovered_plugin_list = []


for discovered_plugin in discovered_plugin_list:
    globals().update({discovered_plugin.name: discovered_plugin.load()})

del entry_points, sys
