import typing

from mutwo import converters
from mutwo import parameters


class TwoPitchesToCommonHarmonicsConverter(converters.abc.Converter):
    """Find the common harmonics between two pitches.

    :param tonality: ``True`` for finding common harmonics, ``False`` for finding
        common subharmonics and ``None`` for finding common pitches between the
        harmonics of the first pitch and the subharmonics of the second pitch.
    :type tonality: typing.Optional[bool]
    :param lowest_partial: The lowest partial to get investigated. Shouldn't be smaller
        than 1.
    :type lowest_partial: int
    :param highest_partial: The highest partial to get investigated. Shouldn't be bigger
        than 1.
    :type highest_partial: int
    """

    def __init__(
        self, tonality: typing.Optional[bool], lowest_partial: int, highest_partial: int
    ):
        self._tonality_per_pitch = (
            (tonality, tonality) if tonality is not None else (True, False)
        )
        self._tonality_to_partials = {
            tonality: TwoPitchesToCommonHarmonicsConverter._make_partials(
                lowest_partial, highest_partial, tonality
            )
            for tonality in (True, False)
        }

    @staticmethod
    def _make_partials(
        lowest_partial: int, highest_partial: int, tonality: bool
    ) -> tuple[parameters.pitches.JustIntonationPitch, ...]:
        partials = tuple(
            (nth_partial, parameters.pitches.JustIntonationPitch(nth_partial, 1))
            for nth_partial in range(lowest_partial, highest_partial)
        )
        if not tonality:
            [partial.inverse() for _, partial in partials]
        return partials

    def convert(
        self,
        pitch_pair_to_examine: tuple[
            parameters.pitches.JustIntonationPitch,
            parameters.pitches.JustIntonationPitch,
        ],
    ) -> tuple[parameters.pitches.CommonHarmonic, ...]:
        partials0, partials1 = tuple(
            tuple(
                (nth_partial, partial + pitch)
                for nth_partial, partial in self._tonality_to_partials[tonality]
            )
            for pitch, tonality in zip(pitch_pair_to_examine, self._tonality_per_pitch)
        )

        nth_partial_for_partials1, partials1 = zip(*partials1)

        common_harmonics = []
        for nth_partial_for_first_pitch, partial in partials0:
            if partial in partials1:
                nth_partial_for_second_pitch = nth_partial_for_partials1[
                    partials1.index(partial)
                ]
                common_harmonic = parameters.pitches.CommonHarmonic(
                    tuple(
                        parameters.pitches.Partial(nth_partial, tonality)
                        for nth_partial, tonality in zip(
                            (nth_partial_for_first_pitch, nth_partial_for_second_pitch),
                            self._tonality_per_pitch,
                        )
                    ),
                    partial,
                )
                common_harmonics.append(common_harmonic)

        return tuple(common_harmonics)
