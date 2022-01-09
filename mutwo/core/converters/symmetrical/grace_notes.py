"""Apply grace notes on Events"""

import copy
import typing

import expenvelope

from mutwo.core import converters
from mutwo.core import events
from mutwo.core import utilities

__all__ = ("GraceNotesConverter",)


class GraceNotesConverter(converters.abc.EventConverter):
    """Apply grace notes and after grace notes on :class:`events.abc.Event`.

    :param minima_grace_notes_duration_factor: Minimal percentage how much
        of the initial duration of the :class:`~mutwo.events.basic.SimpleEvent`
        shall be moved to the grace notes / after grace notes. This value has to be
        smaller than 0.5 (so that the :class:`SimpleEvent` have a
        duration > 0 if it has both: grace notes and after grace notes)
        and bigger than 0 (so that the grace notes or after grace notes
        have a duration > 0). Default to 0.12.
    :type minima_grace_notes_duration_factor: float
    :param maxima_grace_notes_duration_factor: Maxima percentage how much
        of the initial duration of the :class:`~mutwo.events.basic.SimpleEvent`
        shall be moved to the grace notes / after grace notes. This value has to be
        smaller than 0.5 (so that the :class:`SimpleEvent` have a
        duration > 0 if it has both: grace notes and after grace notes)
        and bigger than 0 (so that the grace notes or after grace notes
        have a duration > 0). Default to 0.25.
    :type maxima_grace_notes_duration_factor: float
    :param minima_number_of_grace_notes: For how many events in the grace
        note or after grace note container shall the
        `minima_grace_notes_duration_factor` be applied. Default to 1.
    :type minima_number_of_grace_notes: int
    :param maxima_number_of_grace_notes: For how many events in the grace
        note or after grace note container shall the
        `maxima_number_of_grace_notes` be applied. Default to 4.
    :type maxima_number_of_grace_notes: int
    :param simple_event_to_grace_note_sequential_event: Function which
        receives as an input a :class:`~mutwo.events.basic.SimpleEvent`
        and returns a :class:`~mutwo.events.basic.SequentialEvent`.
        By default the function will ask the event for a
        :attr:`~mutwo.events.music.NoteLike.grace_note_sequential_event`
        attribute, because by default `~mutwo.events.music.NoteLike`
        objects are expected.
    :type simple_event_to_grace_note_sequential_event: typing.Callable[[events.basic.SimpleEvent], events.basic.SequentialEvent[events.basic.SimpleEvent]]
    :param simple_event_to_after_grace_note_sequential_event: Function which
        receives as an input a :class:`~mutwo.events.basic.SimpleEvent`
        and returns a :class:`~mutwo.events.basic.SequentialEvent`.
        By default the function will ask the event for a
        :attr:`~mutwo.events.music.NoteLike.grace_note_sequential_event`
        attribute, because by default `~mutwo.events.music.NoteLike`
        objects are expected.
    :type simple_event_to_after_grace_note_sequential_event: typing.Callable[[events.basic.SimpleEvent], events.basic.SequentialEvent[events.basic.SimpleEvent]]
    """

    def __init__(
        self,
        minima_grace_notes_duration_factor: float = 0.12,
        maxima_grace_notes_duration_factor: float = 0.25,
        minima_number_of_grace_notes: int = 1,
        maxima_number_of_grace_notes: int = 4,
        simple_event_to_grace_note_sequential_event: typing.Callable[
            [events.basic.SimpleEvent],
            events.basic.SequentialEvent[events.basic.SimpleEvent],
        ] = lambda simple_event: simple_event.grace_note_sequential_event,
        simple_event_to_after_grace_note_sequential_event: typing.Callable[
            [events.basic.SimpleEvent],
            events.basic.SequentialEvent[events.basic.SimpleEvent],
        ] = lambda simple_event: simple_event.after_grace_note_sequential_event,
    ):
        self._test_input(
            minima_grace_notes_duration_factor,
            maxima_grace_notes_duration_factor,
            minima_number_of_grace_notes,
            maxima_number_of_grace_notes,
        )

        self._simple_event_to_grace_note_sequential_event = (
            simple_event_to_grace_note_sequential_event
        )
        self._simple_event_to_after_grace_note_sequential_event = (
            simple_event_to_after_grace_note_sequential_event
        )

        self._n_grace_notes_to_grace_note_duration_factor_envelope = (
            expenvelope.Envelope.from_points(
                (minima_number_of_grace_notes, minima_grace_notes_duration_factor),
                (maxima_number_of_grace_notes, maxima_grace_notes_duration_factor),
            )
        )

    @staticmethod
    def _test_input(
        minima_grace_notes_duration_factor: float,
        maxima_grace_notes_duration_factor: float,
        minima_number_of_grace_notes: int,
        maxima_number_of_grace_notes: int,
    ):
        try:
            assert minima_number_of_grace_notes < maxima_number_of_grace_notes
        except AssertionError:
            message = "'minima_number_of_grace_notes' has to be smaller than 'maxima_number_of_grace_notes'!"
            raise ValueError(message)

        try:
            assert (
                minima_grace_notes_duration_factor < maxima_grace_notes_duration_factor
            )
        except AssertionError:
            message = "'minima_grace_notes_duration_factor' has to be smaller than 'maxima_grace_notes_duration_factor'!"
            raise ValueError(message)

        try:
            assert maxima_grace_notes_duration_factor < 0.5
        except AssertionError:
            message = "'maxima_grace_notes_duration_factor' has to be smaller than 0.5!"
            raise ValueError(message)

        try:
            assert minima_grace_notes_duration_factor > 0
        except AssertionError:
            message = "'minima_grace_notes_duration_factor' has to be bigger than 0!"
            raise ValueError(message)

    @staticmethod
    def _get_before_or_after_grace_note_sequential_event(
        simple_event_to_convert: events.basic.SimpleEvent,
        simple_event_to_before_or_after_grace_note_sequential_event: typing.Callable[
            [events.basic.SimpleEvent],
            events.basic.SequentialEvent[events.basic.SimpleEvent],
        ],
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        return utilities.tools.call_function_except_attribute_error(
            simple_event_to_before_or_after_grace_note_sequential_event,
            simple_event_to_convert,
            events.basic.SequentialEvent([]),
        )

    def _get_grace_note_sequential_event(
        self, simple_event_to_convert: events.basic.SimpleEvent
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        return GraceNotesConverter._get_before_or_after_grace_note_sequential_event(
            simple_event_to_convert, self._simple_event_to_grace_note_sequential_event
        )

    def _get_after_grace_note_sequential_event(
        self, simple_event_to_convert: events.basic.SimpleEvent
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        return GraceNotesConverter._get_before_or_after_grace_note_sequential_event(
            simple_event_to_convert,
            self._simple_event_to_after_grace_note_sequential_event,
        )

    def _convert_simple_event(
        self,
        event_to_convert: events.basic.SimpleEvent,
        absolute_entry_delay: utilities.constants.DurationType,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        """Convert instance of :class:`mutwo.events.basic.SimpleEvent`."""

        def adjust_grace_note_sequential_event(
            grace_note_sequential_event: events.basic.SequentialEvent[
                events.basic.SimpleEvent
            ],
        ) -> events.basic.SequentialEvent:
            if grace_note_sequential_event:
                factor_to_main_event = (
                    self._n_grace_notes_to_grace_note_duration_factor_envelope.value_at(
                        len(grace_note_sequential_event)
                    )
                )
                new_duration = event_to_convert.duration * factor_to_main_event
                grace_note_sequential_event = grace_note_sequential_event.copy()
                grace_note_sequential_event.duration = new_duration
            return grace_note_sequential_event

        grace_note_sequential_event = adjust_grace_note_sequential_event(
            self._get_grace_note_sequential_event(event_to_convert)
        )
        after_grace_note_sequential_event = adjust_grace_note_sequential_event(
            self._get_after_grace_note_sequential_event(event_to_convert)
        )

        copied_event_to_convert = copy.deepcopy(event_to_convert)
        # Remove applied grace notes / after grace notes
        copied_event_to_convert.grace_note_sequential_event = (
            events.basic.SequentialEvent([])
        )
        copied_event_to_convert.after_grace_note_sequential_event = (
            events.basic.SequentialEvent([])
        )
        copied_event_to_convert.duration -= (
            grace_note_sequential_event.duration
            + after_grace_note_sequential_event.duration
        )

        grace_note_sequential_event.append(copied_event_to_convert)
        grace_note_sequential_event.extend(after_grace_note_sequential_event)

        return grace_note_sequential_event

    def _convert_simultaneous_event(
        self,
        simultaneous_event: events.basic.SimultaneousEvent,
        absolute_entry_delay: utilities.constants.DurationType,
    ) -> tuple[events.basic.SimultaneousEvent[events.abc.Event]]:
        """Convert instance of :class:`mutwo.events.basic.SimultaneousEvent`."""

        simultaneous_event_copied = simultaneous_event.empty_copy()
        for event in simultaneous_event:
            converted_event = self._convert_event(event, absolute_entry_delay)
            # If we find a simple event, we shouldn't extend but append it to the
            # the SimultaneousEvent. A converted simple event will be a
            # SequentialEvent. The grace notes and after grace notes should
            # happen before and after the respective event. If we extend
            # the whole SequentialEvent to the SimultaneousEvent the
            # grace notes and after grace notes will be played simultaneously
            # with the main note, therefore we have to append them.
            if isinstance(event, events.basic.SimpleEvent):
                simultaneous_event_copied.append(converted_event)
            else:
                simultaneous_event_copied.extend(converted_event)
        return (simultaneous_event_copied,)

    def _convert_sequential_event(
        self,
        sequential_event: events.basic.SequentialEvent,
        absolute_entry_delay: utilities.constants.DurationType,
    ) -> tuple[events.basic.SequentialEvent[events.abc.Event]]:
        sequential_event_copied = sequential_event.empty_copy()
        sequential_event_copied.extend(
            super()._convert_sequential_event(sequential_event, absolute_entry_delay)
        )
        return (sequential_event_copied,)

    def convert(self, event_to_convert: events.abc.Event) -> events.abc.Event:
        """Apply grace notes and after grace notes of all :class:`SimpleEvent`.

        :param event_to_convert: The event which grace notes and after grace
            notes shall be converted to normal events in the upper
            :class:`SequentialEvent`.
        :type event_to_convert: events.abc.Event
        """

        converted_event = self._convert_event(event_to_convert, 0)
        if isinstance(event_to_convert, events.basic.SimpleEvent):
            return converted_event
        else:
            return converted_event[0]
