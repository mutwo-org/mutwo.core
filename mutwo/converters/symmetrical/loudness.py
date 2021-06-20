"""Calculate loudness from amplitude."""

import math

import expenvelope  # type: ignore

import mutwo_third_party
from mutwo import converters
from mutwo.utilities import constants


__all__ = ("LoudnessToAmplitudeConverter",)


class LoudnessToAmplitudeConverter(converters.abc.Converter):
    """Make an approximation of the needed amplitude for a perceived Loudness.

    :param perceived_loudness_in_sone: The subjectively perceived loudness that
        the resulting signal shall have (in the unit `Sone`).
    :param loudspeaker_frequency_response: Optionally the frequency response
        of the used loudspeaker can be added for balancing out uneven curves in
        the loudspeakers frequency response. The frequency response is defined
        with an ``expenvelope.Envelope`` object.
    :param interpolation_order: The interpolation order of the equal loudness
        contour interpolation.

    The converter works best with pure sine waves.
    """

    # roughly the sound of a mosquito flying 3 m away
    # (see https://en.wikipedia.org/wiki/Sound_pressure)
    _auditory_threshold_at_1khz = 0.00002

    def __init__(
        self,
        perceived_loudness_in_sone: constants.Real,
        loudspeaker_frequency_response: expenvelope.Envelope = expenvelope.Envelope.from_points(
            (0, 80), (2000, 80)
        ),
        interpolation_order: int = 4,
    ):
        perceived_loudness_in_phon = self._sone_to_phon(perceived_loudness_in_sone)
        self._equal_loudness_contour_interpolation = mutwo_third_party.pydsm.pydsm.iso226.iso226_spl_itpl(  # type: ignore
            perceived_loudness_in_phon, interpolation_order
        )
        self._loudspeaker_frequency_response = loudspeaker_frequency_response
        self._loudspeaker_frequency_response_average = (
            loudspeaker_frequency_response.average_level()
        )

    # ###################################################################### #
    #                          static methods                                #
    # ###################################################################### #

    @staticmethod
    def _decibel_to_amplitude_ratio(
        decibel: constants.Real, reference_amplitude: constants.Real = 1
    ) -> float:
        return float(reference_amplitude * (10 ** (decibel / 20)))

    @staticmethod
    def _decibel_to_power_ratio(decibel: constants.Real) -> float:
        return float(10 ** (decibel / 10))

    @staticmethod
    def _sone_to_phon(loudness_in_sone: constants.Real) -> constants.Real:
        # formula from http://www.sengpielaudio.com/calculatorSonephon.htm
        if loudness_in_sone >= 1:
            return 40 + (10 * math.log(loudness_in_sone, 2))
        else:
            return 40 * (loudness_in_sone + 0.0005) ** 0.35

    # ###################################################################### #
    #               public methods for interaction with the user             #
    # ###################################################################### #

    def convert(self, frequency: constants.Real) -> constants.Real:
        """Calculates the needed amplitude to reach a particular loudness for the entered frequency.

        :param frequency: A frequency in Hertz for which the necessary amplitude
            shall be calculated.
        :return: Return the amplitude for a sine tone to reach the converters
            loudness when played with the entered frequency.

        **Example:**

        >>> from mutwo.converters import symmetrical
        >>> loudness_converter = symmetrical.loudness.LoudnessToAmplitudeConverter(1)
        >>> loudness_converter.convert(200)
        0.009364120303317933
        >>> loudness_converter.convert(50)
        0.15497924558613232
        """

        # (1) calculates necessary sound pressure level depending on the frequency
        #     and loudness (to get the same loudness over all frequencies)
        sound_pressure_level_for_perceived_loudness_based_on_frequency = float(
            self._equal_loudness_contour_interpolation(frequency)
        )
        # (2) figure out the produced soundpressure of the loudspeaker depending
        #     on the frequency (for balancing uneven frequency responses of
        #     loudspeakers)
        produced_soundpressure_for_1_watt_1_meter_depending_on_loudspeaker = self._loudspeaker_frequency_response.value_at(
            frequency
        )
        difference_to_average = (
            self._loudspeaker_frequency_response_average
            - produced_soundpressure_for_1_watt_1_meter_depending_on_loudspeaker
        )
        sound_pressure_level_for_pereived_loudness_based_on_speaker = (
            sound_pressure_level_for_perceived_loudness_based_on_frequency
            + difference_to_average
        )
        amplitude_ratio = self._decibel_to_amplitude_ratio(
            sound_pressure_level_for_pereived_loudness_based_on_speaker,
            self._auditory_threshold_at_1khz,
        )
        return amplitude_ratio
