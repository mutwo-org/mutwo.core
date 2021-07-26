"""Module for routines which pre- or postprocess abjad containers."""

import abc
import datetime
import typing

import abjad

from mutwo import events
from mutwo import parameters
from mutwo.utilities import constants


class ProcessAbjadContainerRoutine(abc.ABC):
    @abc.abstractmethod
    def __call__(
        self,
        complex_event_to_convert: events.abc.ComplexEvent,
        container_to_process: abjad.Container,
    ):
        raise NotImplementedError


class AddDurationLineEngraver(ProcessAbjadContainerRoutine):
    def __call__(
        self,
        complex_event_to_convert: events.abc.ComplexEvent,
        container_to_process: abjad.Container,
    ):
        container_to_process.consists_commands.append("Duration_line_engraver")


class AddInstrumentName(ProcessAbjadContainerRoutine):
    def __init__(
        self,
        complex_event_to_instrument_name: typing.Callable[
            [events.abc.ComplexEvent], str
        ] = lambda complex_event: complex_event.instrument_name,
        complex_event_to_short_instrument_name: typing.Callable[
            [events.abc.ComplexEvent], str
        ] = lambda complex_event: complex_event.short_instrument_name,
        instrument_name_font_size: str = "teeny",
        short_instrument_name_font_size: str = "teeny",
    ):
        self._complex_event_to_instrument_name = complex_event_to_instrument_name
        self._complex_event_to_short_instrument_name = (
            complex_event_to_short_instrument_name
        )
        self._instrument_name_font_size = instrument_name_font_size
        self._short_instrument_name_font_size = short_instrument_name_font_size

    def __call__(
        self,
        complex_event_to_convert: events.abc.ComplexEvent,
        container_to_process: abjad.Container,
    ):
        first_leaf = abjad.get.leaf(container_to_process[0], 0)

        try:
            instrument_name = self._complex_event_to_instrument_name(
                complex_event_to_convert
            )
        except AttributeError:
            instrument_name = None

        try:
            short_instrument_name = self._complex_event_to_short_instrument_name(
                complex_event_to_convert
            )
        except AttributeError:
            short_instrument_name = None

        lilypond_context = container_to_process.lilypond_context.name

        if instrument_name:
            set_instrument_name_command = (
                f"\\set {lilypond_context}.instrumentName = \\markup {{ "
                f" \\{self._instrument_name_font_size} {{ {instrument_name} }} }}"
            )
            abjad.attach(
                abjad.LilyPondLiteral(set_instrument_name_command), first_leaf,
            )
        if short_instrument_name:
            set_short_instrument_name_command = (
                f"\\set {lilypond_context}.shortInstrumentName = \\markup {{ "
                f" \\{self._short_instrument_name_font_size} {{"
                f" {short_instrument_name} }} }}"
            )
            abjad.attach(
                abjad.LilyPondLiteral(set_short_instrument_name_command), first_leaf,
            )


class AddAccidentalStyle(ProcessAbjadContainerRoutine):
    def __init__(self, accidental_style: str):
        self._accidental_style = accidental_style

    def __call__(
        self,
        complex_event_to_convert: events.abc.ComplexEvent,
        container_to_process: abjad.Container,
    ):
        first_leaf = abjad.get.leaf(container_to_process[0], 0)

        if self._accidental_style:
            abjad.attach(
                abjad.LilyPondLiteral(f'\\accidentalStyle "{self._accidental_style}"'),
                first_leaf,
            )


class AddTimeBracketMarks(ProcessAbjadContainerRoutine):

    # ###################################################################### #
    #                     private static methods                             #
    # ###################################################################### #

    @staticmethod
    def _format_time(time: constants.Real) -> str:
        return format(datetime.timedelta(seconds=round(time)))[2:]

    @staticmethod
    def _attach_time_bracket_mark(
        leaf_to_attach_to: abjad.Leaf,
        time_bracket_mark: abjad.RehearsalMark,
        format_slot: str,
    ):
        abjad.attach(
            abjad.LilyPondLiteral(format(time_bracket_mark), format_slot=format_slot),
            leaf_to_attach_to,
        )

    @staticmethod
    def _add_time_bracket_mark_for_time(
        leaf_to_attach_to: abjad.Leaf,
        time: parameters.abc.DurationType,
        format_slot: str,
    ):
        if format_slot == "after":
            hint = "end at: "
        else:
            hint = "\\hspace #-8 start at: "
        formated_time = AddTimeBracketMarks._format_time(time)
        markup_command = (
            f"\\teeny {{ {hint} }} \\normalsize {{ \\smallCaps {{ {formated_time} "
            " } }"
        )
        time_bracket_mark = abjad.RehearsalMark(markup=abjad.Markup(markup_command))
        AddTimeBracketMarks._attach_time_bracket_mark(
            leaf_to_attach_to, time_bracket_mark, format_slot
        )

    @staticmethod
    def _add_time_bracket_mark_for_time_range(
        leaf_to_attach_to: abjad.Leaf,
        time_range: typing.Tuple[
            parameters.abc.DurationType, parameters.abc.DurationType
        ],
        format_slot: str,
    ):
        if format_slot == "after":
            hint = "\\hspace #-10 end in range: "
        else:
            hint = "\\hspace #-10 start in range: "

        formated_time_range = tuple(
            AddTimeBracketMarks._format_time(time) for time in time_range
        )
        time_bracket_mark = (
            f"\\mark \\markup {{ \\teeny {{ {hint} }} \\normalsize {{ \\smallCaps {{"
            f" {formated_time_range[0]}  }} }} \n\\raise #0.55 \n\\teeny {{ \\concat {{"
            " \\arrow-head #X #LEFT ##t \\draw-line #'(1 . 0) \\arrow-head #X #RIGHT"
            f" ##t }} }}\n\\normalsize {{ \\smallCaps {{ {formated_time_range[1]} }}"
            " } }"
        )
        AddTimeBracketMarks._attach_time_bracket_mark(
            leaf_to_attach_to, time_bracket_mark, format_slot
        )

    @staticmethod
    def _add_time_bracket_mark_for_time_or_time_range(
        leaf_to_attach_to: abjad.Leaf,
        time_or_time_range: events.time_brackets.TimeOrTimeRange,
        format_slot: str,
    ):
        if hasattr(time_or_time_range, "__getitem__"):
            AddTimeBracketMarks._add_time_bracket_mark_for_time_range(
                leaf_to_attach_to, time_or_time_range, format_slot
            )
        else:
            AddTimeBracketMarks._add_time_bracket_mark_for_time(
                leaf_to_attach_to, time_or_time_range, format_slot
            )

    # ###################################################################### #
    #                         private methods                                #
    # ###################################################################### #

    def __call__(
        self,
        complex_event_to_convert: events.time_brackets.TimeBracket,
        container_to_process: abjad.Container,
    ):
        first_leaf = abjad.get.leaf(container_to_process[0], 0)
        last_leaf = abjad.get.leaf(container_to_process[0], -1)
        for leaf_to_attach_to, time_or_time_range, format_slot in (
            (first_leaf, complex_event_to_convert.start_or_start_range, "before",),
            (last_leaf, complex_event_to_convert.end_or_end_range, "after",),
        ):
            # don't add the ending time range for a tempo based time bracket
            # (only rely on the tempo mark in this case!)
            if format_slot != "after" or not isinstance(
                complex_event_to_convert, events.time_brackets.TempoBasedTimeBracket,
            ):
                AddTimeBracketMarks._add_time_bracket_mark_for_time_or_time_range(
                    leaf_to_attach_to, time_or_time_range, format_slot
                )
