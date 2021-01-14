import numbers
import typing
import warnings

from mutwo import converters
from mutwo import parameters

TempoPoint = typing.Union[parameters.tempos.TempoPoint, numbers.Number]


class TempoPointConverter(converters.abc.Converter):
    """Simple class to convert a TempoPoint to beat-length-in-seconds.

    A TempoPoint is defined as an object that has a particular tempo in
    beats per seconds (BPM) and a reference value (1 for a quarter note, 4
    for a whole note, etc.). Besides elaborate mutwo.parameters.tempo.TempoPoint
    objects, any number can also be interpreted as a TempoPoint. In this case
    the number simply represents the BPM number and the reference will be set to 1.
    The returned beat-length-in-seconds always indicates the length for one quarter
    note.
    """

    @staticmethod
    def beats_per_minute_to_seconds_per_beat(beats_per_minute: numbers.Number) -> float:
        return 60 / beats_per_minute

    @staticmethod
    def extract_beats_per_minute_and_reference_from_tempo_point(
        tempo_point: TempoPoint,
    ) -> typing.Tuple[numbers.Number]:
        try:
            beats_per_minute = tempo_point.tempo_in_beats_per_minute
        except AttributeError:
            beats_per_minute = float(tempo_point)

        try:
            reference = tempo_point.reference
        except AttributeError:
            message = (
                "Tempo point {} of type {} doesn't know attribute 'reference'.".format(
                    tempo_point, type(tempo_point)
                )
            )
            message += " Therefore reference has been set to 1."
            warnings.warn(message)
            reference = 1

        return beats_per_minute, reference

    def convert(self, tempo_point_to_convert: TempoPoint) -> float:
        """Converts a TempoPoint to beat-length-in-seconds."""

        (
            beats_per_minute,
            reference,
        ) = self.extract_beats_per_minute_and_reference_from_tempo_point(
            tempo_point_to_convert
        )
        return (
            TempoPointConverter.beats_per_minute_to_seconds_per_beat(beats_per_minute)
            / reference
        )
