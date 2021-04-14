"""Submodule for the parameter volume.

'Volume' is defined as any object that knows a :attr:`amplitude` attribute.
"""

import typing

import numpy as np  # type: ignore

from mutwo import parameters
from mutwo.utilities import constants
from mutwo.utilities import tools

__all__ = ("DirectVolume", "DecibelVolume", "WesternVolume")


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
        ('f', 'pp', 'mf', 'sfz', etc.). For a list of all supported
        indicators, see :const:`mutwo.parameters.volumes_constants.DYNAMIC_INDICATOR`.

    >>> from mutwo.parameters import volumes
    >>> volumes.WesternVolume('fff')
    """

    def __init__(self, name: str):
        self.name = name
        self._standard_dynamic_indicator_to_decibel_mapping = (
            WesternVolume._make_standard_dynamic_indicator_to_decibel_mapping()
        )
        self._dynamic_indicator_to_decibel_mapping = WesternVolume._make_dynamic_indicator_to_decibel_mapping(
            self._standard_dynamic_indicator_to_decibel_mapping
        )
        self._decibel_to_standard_dynamic_indicator_mapping = {
            decibel: dynamic_indicator
            for dynamic_indicator, decibel in self._standard_dynamic_indicator_to_decibel_mapping.items()
        }

    def __repr__(self) -> str:
        return "{}({})".format(type(self).__name__, self.name)

    # ###################################################################### #
    #                      static private methods                            #
    # ###################################################################### #

    @staticmethod
    def _make_standard_dynamic_indicator_to_decibel_mapping() -> typing.Dict[
        str, float
    ]:
        return {
            dynamic_indicator: decibel
            for dynamic_indicator, decibel in zip(
                parameters.volumes_constants.STANDARD_DYNAMIC_INDICATOR,
                np.linspace(
                    parameters.volumes_constants.MINIMUM_DECIBEL_FOR_STANDARD_DYNAMIC_INDICATOR,
                    parameters.volumes_constants.MAXIMUM_DECIBEL_FOR_STANDARD_DYNAMIC_INDICATOR,
                    len(parameters.volumes_constants.STANDARD_DYNAMIC_INDICATOR),
                    dtype=float,
                ),
            )
        }

    @staticmethod
    def _make_dynamic_indicator_to_decibel_mapping(
        standard_dynamic_indicator_to_decibel_mapping: typing.Dict[str, float]
    ) -> typing.Dict[str, float]:
        dynamic_indicator_to_decibel_mapping = {}
        dynamic_indicator_to_decibel_mapping.update(
            standard_dynamic_indicator_to_decibel_mapping
        )
        for (
            special_dynamic_indicator,
            standard_dynamic_indicator,
        ) in (
            parameters.volumes_constants.SPECIAL_DYNAMIC_INDICATOR_TO_STANDARD_DYNAMIC_INDICATOR_MAPPING.items()
        ):
            dynamic_indicator_to_decibel_mapping.update(
                {
                    special_dynamic_indicator: dynamic_indicator_to_decibel_mapping[
                        standard_dynamic_indicator
                    ]
                }
            )
        return dynamic_indicator_to_decibel_mapping

    # ###################################################################### #
    #                class methods (alternative constructors)                #
    # ###################################################################### #

    @classmethod
    def from_amplitude(cls, amplitude: constants.Real) -> "WesternVolume":
        """Initialise `WesternVolume` from amplitude ratio.

        :param amplitude: The amplitude which shall be converted to a `WesternVolume`
            object.

        >>> from mutwo.parameters import volumes
        >>> volumes.WesternVolume.from_amplitude(0.05)
        WesternVolume(mp)
        """
        decibel = cls.amplitude_ratio_to_decibel(amplitude)
        return cls.from_decibel(decibel)

    @classmethod
    def from_decibel(cls, decibel: constants.Real) -> "WesternVolume":
        """Initialise `WesternVolume` from decibel.

        :param decibel: The decibel which shall be converted to a `WesternVolume`
            object.

        >>> from mutwo.parameters import volumes
        >>> volumes.WesternVolume.from_decibel(-24)
        WesternVolume(mf)
        """
        volume_object = cls("mf")
        closest_decibel: float = tools.find_closest_item(
            decibel,
            tuple(volume_object._decibel_to_standard_dynamic_indicator_mapping.keys()),
        )
        indicator = volume_object._decibel_to_standard_dynamic_indicator_mapping[
            closest_decibel
        ]
        volume_object.name = indicator
        return volume_object

    # ###################################################################### #
    #                             properties                                 #
    # ###################################################################### #

    @property
    def name(self) -> str:
        """The western nomenclature name for dynamic.

        For a list of all supported indicators, see
        :const:`mutwo.parameters.volumes_constants.DYNAMIC_INDICATOR`.
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        try:
            assert name in parameters.volumes_constants.DYNAMIC_INDICATOR
        except AssertionError:
            message = (
                "unknown dynamic name '{}'. Supported dynamic names are '{}'.".format(
                    name, parameters.volumes_constants.DYNAMIC_INDICATOR,
                )
            )
            raise ValueError(message)
        self._name = name

    @property
    def decibel(self) -> constants.Real:
        return self._dynamic_indicator_to_decibel_mapping[self.name]

    @property
    def amplitude(self) -> constants.Real:
        return self.decibel_to_amplitude_ratio(self.decibel)
