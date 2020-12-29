import math
import numbers
import pydsm

import expenvelope

from mutwo import converters


class LoudnessToAmplitudeConverter(converters.abc.ParameterConverter):
    """Make an approximation of the needed amplitude for a perceived Loudness.

    The respective values only work with pure sine waves.
    """

    # roughly the sound of a mosquito flying 3 m away
    _auditory_threshold_at_1khz = 0.00002

    def __init__(
        self,
        perceived_loudness_in_sone: numbers.Number,
        loudspeaker_frequency_response: expenvelope.Envelope = expenvelope.Envelope.from_points(
            (0, 80), (2000, 80)
        ),
        interpolation_order: int = 4,
    ):
        perceived_loudness_in_phon = self.convert_sone_to_phon(
            perceived_loudness_in_sone
        )
        self._equal_loudness_contour_interpolation = pydsm.iso226.iso226_spl_itpl(
            perceived_loudness_in_phon, interpolation_order
        )
        self._loudspeaker_frequency_response = loudspeaker_frequency_response
        self._loudspeaker_frequency_response_maxima = (
            loudspeaker_frequency_response.max_level()
        )

    @staticmethod
    def convert_decibel_to_amplitude_ratio(
        decibel: numbers.Number, reference_amplitude: numbers.Number = 1
    ) -> float:
        return float(reference_amplitude * (10 ** (decibel / 20)))

    @staticmethod
    def convert_decibel_to_power_ratio(decibel: numbers.Number) -> float:
        return float(10 ** (decibel / 10))

    @staticmethod
    def convert_sone_to_phon(loudness_in_sone: numbers.Number) -> numbers.Number:
        # formula from http://www.sengpielaudio.com/calculatorSonephon.htm
        if loudness_in_sone >= 1:
            return 40 + (10 * math.log(loudness_in_sone, 2))
        else:
            return 40 * (loudness_in_sone + 0.0005) ** 0.35

    def convert(self, frequency: numbers.Number) -> numbers.Number:
        # (1) calculates necessary sound pressure level depending on the frequency
        #     and loudness (to get the same loudness over all frequencies)
        sound_pressure_level_for_perceived_loudness_based_on_frequency = float(
            self._equal_loudness_contour_interpolation(frequency)
        )
        # (2) figure out the produced soundpressure of the loudspeaker depending
        #     on the frequency
        produced_soundpressure_for_1_watt_1_meter_depending_on_loudspeaker = self._loudspeaker_frequency_response.value_at(
            frequency
        )
        difference_to_maxima = (
            self._loudspeaker_frequency_response_maxima
            - produced_soundpressure_for_1_watt_1_meter_depending_on_loudspeaker
        )
        sound_pressure_level_for_pereived_loudness_based_on_speaker = (
            sound_pressure_level_for_perceived_loudness_based_on_frequency
            + difference_to_maxima
        )
        amplitude_ratio = self.convert_decibel_to_amplitude_ratio(
            sound_pressure_level_for_pereived_loudness_based_on_speaker,
            self._auditory_threshold_at_1khz,
        )
        return amplitude_ratio
