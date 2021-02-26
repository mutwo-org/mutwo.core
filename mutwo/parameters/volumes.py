"""Submodule for the parameter volume.

'Volume' is defined as any object that knows a 'amplitude' attribute.
"""

import numbers

from mutwo import parameters

__all__ = ("DirectVolume",)


class DirectVolume(parameters.abc.Volume):
    """A simple volume class that gets directly initialised by its amplitude.

    :param amplitude: The amplitude of the ``DirectVolume`` object.

    May be used when a converter class needs a volume object, but there is
    no need or desire for a complex abstraction of the respective volume.
    """
    def __init__(self, amplitude: numbers.Number):
        self._amplitude = amplitude

    @property
    def amplitude(self) -> numbers.Number:
        return self._amplitude

    def __repr__(self) -> str:
        return "DirectVolume({})".format(self.amplitude)
