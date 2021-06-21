"""Render signing signals from mutwo data via `ISiS <https://forum.ircam.fr/projects/detail/isis/>`_.

ISiS (IRCAM Singing Synthesis) is a `"command line application for singing
synthesis that can be used to generate singing signals by means of synthesizing
them from melody and lyrics."
<https://isis-documentation.readthedocs.io/en/latest/Intro.html#the-isis-command-line>`_.
"""

import os
import typing

from mutwo import events

from mutwo import converters
from mutwo.converters.frontends import isis_constants
from mutwo import parameters
from mutwo.utilities import constants

__all__ = ("IsisScoreConverter", "IsisConverter")

ConvertableEvents = typing.Union[
    events.basic.SimpleEvent, events.basic.SequentialEvent[events.basic.SimpleEvent],
]
ExtractedData = typing.Tuple[
    # duration, consonants, vowel, pitch, volume
    parameters.abc.DurationType,
    typing.Tuple[str, ...],
    str,
    parameters.abc.Pitch,
    parameters.abc.Volume,
]


class IsisScoreConverter(converters.abc.EventConverter):
    """Class to convert mutwo events to a `ISiS score file. <https://isis-documentation.readthedocs.io/en/latest/score.html>`_

    :param path: where to write the ISiS score file
    :param simple_event_to_pitch: Function to extract an instance of
        :class:`mutwo.parameters.abc.Pitch` from a simple event.
    :param simple_event_to_volume:
    :param simple_event_to_vowel:
    :param simple_event_to_consonants:
    :param is_simple_event_rest:
    :param tempo: Tempo in beats per minute (BPM). Defaults to 60.
    :param global_transposition: global transposition in midi numbers. Defaults to 0.
    :param n_events_per_line: How many events the score shall contain per line.
        Defaults to 5.
    """

    def __init__(
        self,
        path: str,
        simple_event_to_pitch: typing.Callable[
            [events.basic.SimpleEvent], parameters.abc.Pitch
        ] = lambda simple_event: simple_event.pitch_or_pitches[
            0
        ],  # type: ignore
        simple_event_to_volume: typing.Callable[
            [events.basic.SimpleEvent], parameters.abc.Volume
        ] = lambda simple_event: simple_event.volume,  # type: ignore
        simple_event_to_vowel: typing.Callable[
            [events.basic.SimpleEvent], str
        ] = lambda simple_event: simple_event.vowel,  # type: ignore
        simple_event_to_consonants: typing.Callable[
            [events.basic.SimpleEvent], typing.Tuple[str, ...]
        ] = lambda simple_event: simple_event.consonants,  # type: ignore
        is_simple_event_rest: typing.Callable[
            [events.basic.SimpleEvent], bool
        ] = lambda simple_event: not (
            hasattr(simple_event, "pitch_or_pitches") and simple_event.pitch_or_pitches
        ),
        tempo: constants.Real = 60,
        global_transposition: int = 0,
        default_sentence_loudness: typing.Union[constants.Real, None] = None,
        n_events_per_line: int = 5,
    ):
        self.path = path
        self._tempo = tempo
        self._global_transposition = global_transposition
        self._default_sentence_loudness = default_sentence_loudness
        self._n_events_per_line = n_events_per_line
        self._is_simple_event_rest = is_simple_event_rest

        self._extraction_functions = (
            simple_event_to_consonants,
            simple_event_to_vowel,
            simple_event_to_pitch,
            simple_event_to_volume,
        )

    # ###################################################################### #
    #                           private methods                              #
    # ###################################################################### #

    def _make_key_from_extracted_data_per_event(
        self,
        key_name: str,
        extracted_data_per_event: typing.Tuple[ExtractedData],
        key: typing.Callable[[ExtractedData], typing.Tuple[str, ...]],
        seperate_with_comma: bool = True,
    ) -> str:
        objects_per_line: typing.List[typing.List[str]] = [[]]
        for nth_event, extracted_data in enumerate(extracted_data_per_event):
            objects_per_line[-1].extend(key(extracted_data))
            if nth_event % self._n_events_per_line == 0:
                objects_per_line.append([])

        object_join_string = ", " if seperate_with_comma else " "
        lines = [object_join_string.join(line) for line in objects_per_line if line]

        line_join_string = ",\n" if seperate_with_comma else "\n"
        line_join_string = "{}{}".format(line_join_string, " " * (len(key_name) + 2))

        return "{}: {}".format(key_name, line_join_string.join(lines))

    def _make_lyrics_section_from_extracted_data_per_event(
        self, extracted_data_per_event: typing.Tuple[ExtractedData],
    ) -> str:
        xsampa = self._make_key_from_extracted_data_per_event(
            "xsampa",
            extracted_data_per_event,
            lambda extracted_data: extracted_data[1] + (extracted_data[2],),
            False,
        )

        lyric_section = "[lyrics]\n{}".format(xsampa)
        return lyric_section

    def _make_score_section_from_extracted_data_per_event(
        self, extracted_data_per_event: typing.Tuple[ExtractedData],
    ) -> str:
        midi_notes = self._make_key_from_extracted_data_per_event(
            "midiNotes",
            extracted_data_per_event,
            lambda extracted_data: (str(extracted_data[3].midi_pitch_number),),
        )
        rhythm = self._make_key_from_extracted_data_per_event(
            "rhythm",
            extracted_data_per_event,
            lambda extracted_data: (str(extracted_data[0]),),
        )
        loud_accents = self._make_key_from_extracted_data_per_event(
            "loud_accents",
            extracted_data_per_event,
            lambda extracted_data: (str(extracted_data[4].amplitude),),
        )
        score_section = (
            "[score]\n{}\nglobalTransposition: {}\n{}\n{}\ntempo: {}".format(
                midi_notes,
                self._global_transposition,
                rhythm,
                loud_accents,
                self._tempo,
            )
        )
        return score_section

    def _convert_simple_event(
        self,
        simple_event_to_convert: events.basic.SimpleEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> typing.Tuple[ExtractedData]:
        duration = simple_event_to_convert.duration

        extracted_data: typing.List[object] = [duration]
        for extraction_function in self._extraction_functions:
            try:
                extracted_information = extraction_function(simple_event_to_convert)
            except AttributeError:
                return (
                    (
                        duration,
                        tuple([]),
                        "_",
                        parameters.pitches.WesternPitch(
                            "c",
                            -1,
                            concert_pitch=440,
                            concert_pitch_octave=4,
                            concert_pitch_pitch_class=9,
                        ),
                        parameters.volumes.DirectVolume(0),
                    ),
                )

            extracted_data.append(extracted_information)

        return (tuple(extracted_data),)  # type: ignore

    def _convert_simultaneous_event(
        self,
        simultaneous_event_to_convert: events.basic.SimultaneousEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ):
        message = (
            "Can't convert instance of SimultaneousEvent to ISiS Score. ISiS is only a"
            " monophonic synthesizer and can't read multiple simultaneous voices!"
        )
        raise NotImplementedError(message)

    # ###################################################################### #
    #                             public api                                 #
    # ###################################################################### #

    def convert(self, event_to_convert: ConvertableEvents) -> None:
        """Render ISiS score file from the passed event.

        :param event_to_convert: The event that shall be rendered to a ISiS score
            file.

        **Example:**

        >>> from mutwo.events import events.basic, music
        >>> from mutwo.parameters import pitches
        >>> from mutwo.converters.frontends import isis
        >>> notes = events.basic.SequentialEvent(
        >>>    [
        >>>         music.NoteLike(pitches.WesternPitch(pitch_name), 0.5, 0.5)
        >>>         for pitch_name in 'c f d g'.split(' ')
        >>>    ]
        >>> )
        >>> for consonants, vowel, note in zip([[], [], ['t'], []], ['a', 'o', 'e', 'a'], notes):
        >>>     note.vowel = vowel
        >>>     note.consonants = consonants
        >>> isis_score_converter = isis.IsisScoreConverter('my_singing_score')
        >>> isis_score_converter.convert(notes)
        """

        if isinstance(event_to_convert, events.abc.ComplexEvent):
            event_to_convert = event_to_convert.tie_by(
                lambda event0, event1: self._is_simple_event_rest(event0)
                and self._is_simple_event_rest(event1),
                event_type_to_examine=events.basic.SimpleEvent,
                mutate=False,
            )

        extracted_data_per_event = self._convert_event(event_to_convert, 0)
        lyrics_section = self._make_lyrics_section_from_extracted_data_per_event(
            extracted_data_per_event  # type: ignore
        )
        score_section = self._make_score_section_from_extracted_data_per_event(
            extracted_data_per_event  # type: ignore
        )
        with open(self.path, "w") as f:
            f.write("\n\n".join([lyrics_section, score_section]))


class IsisConverter(converters.abc.Converter):
    """Generate audio files with `ISiS <https://forum.ircam.fr/projects/detail/isis/>`_.

    :param path: where to write the sound file
    :param isis_score_converter: The :class:`IsisScoreConverter` that shall be used
        to render the ISiS score file from a mutwo event.
    :param *flag: Flag that shall be added when calling ISiS. Several of the supported
        ISiS flags can be found in :mod:`mutwo.converters.frontends.isis_constants`.
    :param remove_score_file: Set to True if :class:`IsisConverter` shall remove the
        ISiS score file after rendering. Defaults to False.

    **Disclaimer:** Before using the :class:`IsisConverter`, make sure ISiS has been
    correctly installed on your system.
    """

    def __init__(
        self,
        path: str,
        isis_score_converter: IsisScoreConverter,
        *flag: str,
        remove_score_file: bool = False
    ):
        self.flags = flag
        self.path = path
        self.isis_score_converter = isis_score_converter
        self.remove_score_file = remove_score_file

    def convert(self, event_to_convert: ConvertableEvents) -> None:
        """Render sound file via ISiS from mutwo event.

        :param event_to_convert: The event that shall be rendered.


        **Disclaimer:** Before using the :class:`IsisConverter`, make sure
        `ISiS <https://forum.ircam.fr/projects/detail/isis/>`_ has been
        correctly installed on your system.
        """

        self.isis_score_converter.convert(event_to_convert)
        command = "{} -m {} -o {}".format(
            isis_constants.ISIS_PATH, self.isis_score_converter.path, self.path,
        )
        for flag in self.flags:
            command += " {} ".format(flag)

        os.system(command)

        if self.remove_score_file:
            os.remove(self.isis_score_converter.path)
