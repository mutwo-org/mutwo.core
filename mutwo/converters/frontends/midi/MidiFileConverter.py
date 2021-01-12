import abc
import numbers
import typing

import mido

from mutwo.converters.frontends import abc as converters_frontends_abc
from mutwo.converters.frontends import midi
from mutwo import events
from mutwo import parameters

Cents = typing.NewType("Cents", numbers.Number)

ConvertableEvents = typing.Union[
    events.music.NoteLike,
    events.basic.SequentialEvent[events.music.NoteLike],
    events.basic.SimultaneousEvent[events.basic.SequentialEvent[events.music.NoteLike]],
]


class MidiFileConverter(converters_frontends_abc.FileConverter):
    """Class for rendering midi files from mutwo data.

    :param path: where to write the MidiFile
    :param simple_event_to_pitches: Function to extract from a SimpleEvent a tuple
        that contains pitch objects while generating midi notes. By default it asks the
        Event for its 'pitch_or_pitches' attribute (because by default
        mutwo.events.music.NoteLike objects are expected). When using different Event
        classes than NoteLike with a different name for their pitch property this
        argument should be overridden. If the function call raises an AttributeError
        (e.g. if no pitch can be extracted) mutwo will interpret the event as a rest.
    :param simple_event_to_volume: Function to extract the volume from a SimpleEvent
        in the purpose of generating midi notes. The volume should be a number from
        0 to 1 (where 0 represents velocity 0 and 1 represents velocity 127).
        Higher and lower values will be clipped. By default it asks the Event for its
        'volume' attribute (because by default mutwo.events.music.NoteLike objects are
        expected). When using different Event classes than NoteLike with a different
        name for their volume property this argument should be overridden. If the
        function call raises an AttributeError (e.g. if no volume can be extracted)
        mutwo will interpret the event as a rest.
    :param simple_event_to_control_messages: Function to generate midi control messages
        from a simple event. By default no control messages are generated. If the
        function call raises an AttributeError (e.g. if an expected control value isn't
        available) mutwo will interpret the event as a rest.
    :param available_midi_channels: tuple containing integer where each integer
        represents the number of the used midi channel. Integer can range from 0 to 15.
        Higher numbers of available_midi_channels (like all 16) are recommended when
        rendering microtonal music.
    :param maximum_pitch_bend_deviation: sets the maximum pitch bending range in cents.
        This value depends on the particular used software synthesizer and
        its settings, because its up to the respective synthesizer how to interpret
        the pitch bending messages. By default mutwo sets the value to 200 cents which
        seems to be the most common interpretation.
    :param ticks_per_beat: Sets the timing precision of the midi file. From the mido
        documentation: "Typical values range from 96 to 480 but some use even more
        ticks per beat."
    :param instrument_name: Sets the midi instrument of all tracks.
    """

    def __init__(
        self,
        path: str,  # where to write the midi file
        simple_event_to_pitches: typing.Callable[
            [events.basic.SimpleEvent], typing.Tuple[parameters.pitches.abc.Pitch]
        ] = lambda event: event.pitch_or_pitches,
        # function to get the events volume
        simple_event_to_volume: typing.Callable[
            [events.basic.SimpleEvent], numbers.Number
        ] = lambda event: event.volume,
        # if additional control messages are desired
        simple_event_to_control_messages: typing.Callable[
            [events.basic.SimpleEvent], typing.Tuple[mido.Message]
        ] = lambda event: tuple([]),
        available_midi_channels: typing.Iterable[int] = None,
        maximum_pitch_bend_deviation: Cents = None,  # depends on synthesizer
        ticks_per_beat: int = None,  # sets time precision
        instrument_name: str = None,  # midi instrument name
        # function to get the events pitch
        tempo_events: typing.Union[
            events.basic.SequentialEvent[events.basic.EnvelopeEvent], None
        ] = None,
    ):
        # set current default values if not defined
        if available_midi_channels is None:
            available_midi_channels = midi.constants.DEFAULT_AVAILABLE_MIDI_CHANNELS

        if maximum_pitch_bend_deviation is None:
            maximum_pitch_bend_deviation = (
                midi.constants.DEFAULT_MAXIMUM_PITCH_BEND_DEVIATION_IN_CENTS
            )

        if ticks_per_beat is None:
            ticks_per_beat = midi.constants.DEFAULT_TICKS_PER_BEAT

        if instrument_name is None:
            instrument_name = midi.constants.DEFAULT_MIDI_INSTRUMENT_NAME

        if tempo_events is None:
            tempo_events = events.basic.SequentialEvent(
                [events.basic.TempoEvent(1, 60)]
            )

        self.path = path
        self._simple_event_to_pitches = simple_event_to_pitches
        self._simple_event_to_volume = simple_event_to_volume
        self._simple_event_to_control_messages = simple_event_to_control_messages
        self._available_midi_channels = available_midi_channels
        self._tempo_events = tempo_events
        self._maximum_pitch_bend_deviation = maximum_pitch_bend_deviation
        self._ticks_per_beat = ticks_per_beat
        self._tick_size = 1 / self._ticks_per_second
        self._instrument_name = instrument_name

    @abc.abstractmethod
    def _tune_pitch(self, pitch: parameters.pitches.abc.Pitch):
        raise NotImplementedError

    def _convert_seconds_to_ticks(self, n_seconds: numbers.Number) -> int:
        return int(n_seconds // self._tick_size)

    def _convert_simple_event_to_midi_messages(
        self, simple_event: events.basic.SimpleEvent
    ) -> typing.Tuple[mido.Message]:

        extracted_data = []

        # try to extract the relevant data
        is_rest = False
        for extraction_function in (
            self._simple_event_to_pitches,
            self._simple_event_to_volume,
            self._simple_event_to_control_messages,
        ):
            try:
                extracted_data.append(extraction_function(simple_event))
            except AttributeError:
                is_rest = True

        # if not all relevant data could be extracted, make a rest
        if is_rest:
            pass

        else:
            pass

    def _convert_sequential_event_to_midi_track(
        self, sequential_event: events.basic.SequentialEvent[events.basic.SimpleEvent]
    ) -> mido.MidiTrack:
        # initialise midi track
        track = mido.MidiTrack([])
        track.append(mido.MetaMessage("instrument_name", name=self._instrument_name))

        # fill midi track with the content of the sequential event
        for simple_event in sequential_event:
            midi_messages = self._convert_simple_event_to_midi_messages(simple_event)
            track.extend(midi_messages)

        # add end of track message
        track.append(mido.MetaMessage("end_of_track"))
        return track

    def _convert_simultaneous_event_to_midi_tracks(
        self,
        simultaneous_event: events.basic.SimultaneousEvent[
            events.basic.SequentialEvent[events.music.NoteLike]
        ],
    ) -> typing.Tuple[mido.MidiTrack]:
        return tuple(
            self._convert_sequential_event_to_midi_track(sequential_event)
            for sequential_event in simultaneous_event
        )

    def convert(self, event_to_convert: ConvertableEvents) -> None:
        """Render a Midi file from the given event.

        :param event_to_convert: The given event that shall be translated
            to a Midi file.

        Disclaimer: when passing nested structures, make sure that the
        nested object matches the expected type. Unlike other mutwo
        converter classes (like TempoConverter) MidiFileConverter can't
        convert infinite nested structures (due to the particular
        way how Midi files are defined). The deepest potential structure
        is a SimultaneousEvent (representing the complete MidiFile) that
        contains SequentialEvents (where each SequentialEvent represents
        one MidiTrack) that contains SimpleEvents (where each SimpleEvent
        or NoteLike object represents one midi note).
        """

        midi_file = mido.MidiFile([], ticks_per_beat=self._ticks_per_beat)

        # depending on the event type different methods are called
        if isinstance(event_to_convert, events.basic.SimultaneousEvent):
            midi_file.extend(
                self._convert_simultaneous_event_to_midi_tracks(event_to_convert)
            )
        elif isinstance(event_to_convert, events.basic.SequentialEvent):
            midi_file.append(
                self._convert_sequential_event_to_midi_track(event_to_convert)
            )
        elif isinstance(event_to_convert, events.basic.SimpleEvent):
            midi_file.append(
                self._convert_sequential_event_to_midi_track(
                    events.basic.SequentialEvent([event_to_convert])
                )
            )
        else:
            message = "Can't convert object '{}' of type '{}' to a MidiFile.".format(
                event_to_convert, type(event_to_convert)
            )
            message += " Supported types include '{}'.".format(ConvertableEvents)
            raise TypeError(message)

        midi_file.save(filename=self.path)
