"""Submodule for the parameter volume.

'Volume' is defined as any object that knows a :attr:`amplitude` attribute.
"""


from mutwo import parameters
from mutwo.utilities import constants
from mutwo.utilities import tools

__all__ = ("DirectVolume", "DecibelVolume")


class DirectVolume(parameters.abc.Volume):
    """A simple volume class that gets directly initialised by its amplitude.

    :param amplitude: The amplitude of the :class:`DirectVolume` object.

    May be used when a converter class needs a volume object, but there is
    no need or desire for a complex abstraction of the respective volume.
    """

    def __init__(self, amplitude: constants.Real):
        self._amplitude = amplitude

    @property
    def amplitude(self) -> constants.Real:
        return self._amplitude

    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, self.amplitude)


class DecibelVolume(parameters.abc.Volume):
    """A simple volume class that gets directly initialised by decibel.

    :param decibel: The decibel of the :class:`DecibelVolume` object (should be
        from -120 to 0).

    May be used when a converter class needs a volume object, but there is
    no need or desire for a complex abstraction of the respective volume.
    """

    def __init__(self, decibel: constants.Real):
        self._decibel = decibel

    @property
    def decibel(self) -> constants.Real:
        return self._decibel

    @property
    def amplitude(self) -> constants.Real:
        return self.decibel_to_amplitude_ratio(self.decibel)

    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, self.amplitude)


class WesternVolume(parameters.abc.Volume):
    """Volume with a traditional Western nomenclature.

    :param name: Dynamic indicator in traditional Western nomenclature
        ('f', 'pp', 'mf', 'sfz', etc.).

    >>> from mutwo.parameters import volumes
    >>> volumes.WesternVolume('fff')
    """

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, self.name)

    @classmethod
    def from_amplitude(cls, amplitude: constants.Real) -> "WesternVolume":
        decibel = cls.amplitude_ratio_to_decibel(amplitude)
        return cls.from_decibel(decibel)

    @classmethod
    def from_decibel(cls, decibel: constants.Real) -> "WesternVolume":
        closest_decibel: constants.Real = tools.find_closest_item(
            decibel,
            tuple(parameters.volumes_constants.DECIBEL_TO_STANDARD_DYNAMIC_INDICATOR.keys()),
        )
        indicator = parameters.volumes_constants.DECIBEL_TO_STANDARD_DYNAMIC_INDICATOR[
            closest_decibel
        ]
        return cls(indicator)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        try:
            assert name in parameters.volumes_constants.DYNAMIC_INDICATOR_TO_DECIBEL
        except AssertionError:
            message = (
                "Unknown dynamic name '{}'. Supported dynamic names are '{}'.".format(
                    name,
                    parameters.volumes_constants.DYNAMIC_INDICATOR_TO_DECIBEL.keys(),
                )
            )
            raise ValueError(message)
        self._name = name

    @property
    def decibel(self) -> constants.Real:
        return parameters.volumes_constants.DYNAMIC_INDICATOR_TO_DECIBEL[self.name]

    @property
    def amplitude(self) -> constants.Real:
        return self.decibel_to_amplitude_ratio(self.decibel)
