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
    :type name: str
    :param minimum_decibel: The decibel value which is equal to the lowest dynamic indicator
        (ppppp).
    :type minimum_decibel: constants.Real, optional
    :param maximum_decibel: The decibel value which is equal to the highest dynamic indicator
        (fffff).
    :type maximum_decibel: constants.Real, optional

    **Example:**

    >>> from mutwo.parameters import volumes
    >>> volumes.WesternVolume('fff')
    WesternVolume(fff)
    """

    def __init__(
        self,
        name: str,
        minimum_decibel: typing.Optional[constants.Real] = None,
        maximum_decibel: typing.Optional[constants.Real] = None,
    ):
        if minimum_decibel is None:
            minimum_decibel = (
                parameters.volumes_constants.DEFAULT_MINIMUM_DECIBEL_FOR_MIDI_VELOCITY_AND_STANDARD_DYNAMIC_INDICATOR
            )

        if maximum_decibel is None:
            maximum_decibel = (
                parameters.volumes_constants.DEFAULT_MAXIMUM_DECIBEL_FOR_MIDI_VELOCITY_AND_STANDARD_DYNAMIC_INDICATOR
            )

        self.name = name
        self._standard_dynamic_indicator_to_decibel_mapping = WesternVolume._make_standard_dynamic_indicator_to_value_mapping(
            minimum_decibel, maximum_decibel, float,
        )
        self._dynamic_indicator_to_decibel_mapping = WesternVolume._make_dynamic_indicator_to_value_mapping(
            self._standard_dynamic_indicator_to_decibel_mapping
        )
        self._decibel_to_standard_dynamic_indicator_mapping = {
            decibel: dynamic_indicator
            for dynamic_indicator, decibel in self._standard_dynamic_indicator_to_decibel_mapping.items()
        }

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name})"

    # ###################################################################### #
    #                      static private methods                            #
    # ###################################################################### #

    @staticmethod
    def _make_standard_dynamic_indicator_to_value_mapping(
        minima: float, maxima: float, dtype: typing.Type[float] = float
    ) -> typing.Dict[str, float]:
        return {
            dynamic_indicator: decibel
            for dynamic_indicator, decibel in zip(
                parameters.volumes_constants.STANDARD_DYNAMIC_INDICATOR,
                np.linspace(
                    minima,
                    maxima,
                    len(parameters.volumes_constants.STANDARD_DYNAMIC_INDICATOR),
                    dtype=dtype,
                ),
            )
        }

    @staticmethod
    def _make_dynamic_indicator_to_value_mapping(
        standard_dynamic_indicator_to_value_mapping: typing.Dict[str, float]
    ) -> typing.Dict[str, float]:
        dynamic_indicator_to_value_mapping = {}
        dynamic_indicator_to_value_mapping.update(
            standard_dynamic_indicator_to_value_mapping
        )
        for (
            special_dynamic_indicator,
            standard_dynamic_indicator,
        ) in (
            parameters.volumes_constants.SPECIAL_DYNAMIC_INDICATOR_TO_STANDARD_DYNAMIC_INDICATOR_MAPPING.items()
        ):
            dynamic_indicator_to_value_mapping.update(
                {
                    special_dynamic_indicator: dynamic_indicator_to_value_mapping[
                        standard_dynamic_indicator
                    ]
                }
            )
        return dynamic_indicator_to_value_mapping

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
