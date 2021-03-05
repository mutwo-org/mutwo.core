"""Submodule for the parameter volume.

'Volume' is defined as any object that knows a :attr:`amplitude` attribute.
"""

import numbers

from mutwo import parameters

__all__ = ("DirectVolume", "DecibelVolume")


class DirectVolume(parameters.abc.Volume):
    """A simple volume class that gets directly initialised by its amplitude.

    :param amplitude: The amplitude of the :class:`DirectVolume` object.

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


class DecibelVolume(parameters.abc.Volume):
    """A simple volume class that gets directly initialised by decibel.

    :param decibel: The decibel of the :class:`DecibelVolume` object (should be
        from -120 to 0).

    May be used when a converter class needs a volume object, but there is
    no need or desire for a complex abstraction of the respective volume.
    """

    def __init__(self, decibel: numbers.Number):
        self._decibel = decibel

    @property
    def decibel(self) -> numbers.Number:
        return self._decibel

    @property
    def amplitude(self) -> numbers.Number:
        return self.decibel_to_amplitude_ratio(self.decibel)

    def __repr__(self) -> str:
        return "DecibelVolume({})".format(self.amplitude)


class WesternVolume(parameters.abc.Volume):
    def __init__(self, indication: str):
        raise NotImplementedError
