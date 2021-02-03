import numbers
import typing
import warnings

import natsort

from mutwo.converters.frontends import abc as converters_frontends_abc
from mutwo import events
from mutwo import parameters

SupportedPFieldTypes = typing.Union[numbers.Number, str]
PFieldFunction = typing.Callable[[events.basic.SimpleEvent], SupportedPFieldTypes]
ConvertableEvent = typing.Union[
    events.basic.SimpleEvent,
    events.basic.SequentialEvent,
    events.basic.SimultaneousEvent,
]


class CsoundScoreConverter(converters_frontends_abc.FileConverter):
    """Class to convert mutwo events to a Csound score file.

        :param path: The path of the csound score file that shall be generated.
        :param pfield: p-field / p-field-extraction-function pairs.

    This class helps generating score files for the "domain-specific computer
    programming language for audio programming" Csound (see http://www.csounds.com/).

    CsoundScoreConverter extracts data from mutwo Events and assign it to
    specific p-fields. The mapping of Event attributes to p-field values has
    to be defined by the user via keyword arguments during class initialization.
    By default mutwo already maps the following p-fields to the following values:
    - p1 (instrument name) to 1
    - p2 (start time) to the absolute start time of the event
    - p3 (duration) to the duration attribute of the event

    If p2 shall be assigned to the absolute entry delay of the event,
    it has to be set to None.

    The CsoundScoreConverter ignores any p-field that returns
    any unsupported p-field type (anything else than a string
    or a number). If the returned type is a string, CsoundScoreConverter
    automatically adds quotations marks around the string in the score file.

    All p fields can be overwritten in the following manner:

    >>> my_converter = CsoundScoreConverter(path="my_csound_score.sco", p1=lambda event: 2, p4=lambda event: event.pitch.frequency, p5=lambda event: event.volume)
    """

    def __init__(
        self,
        path: str,
        p1: PFieldFunction = lambda event: 1,  # default instrument name "1"
        p2: typing.Union[PFieldFunction, None] = None,  # default to absolute start time
        p3: PFieldFunction = lambda event: event.duration,  # default key for duration
        **pfield: PFieldFunction
    ):
        pfield.update({"p1": p1, "p2": p2, "p3": p3})
        self.pfields = self._generate_pfield_mapping(pfield)
        self.path = path

    @staticmethod
    def _generate_pfield_mapping(
        pfield_key_to_function_mapping: dict,
    ) -> typing.Tuple[PFieldFunction]:
        """Maps p-fields to their respective p_field_function."""

        sorted_pfield_keys = natsort.natsorted(pfield_key_to_function_mapping.keys())
        pfields = []
        for key0, key1 in zip(sorted_pfield_keys, sorted_pfield_keys[1:]):
            number0, number1 = (int(pfield_name[1:]) for pfield_name in (key0, key1))
            try:
                assert number0 >= 0
            except AssertionError:
                message = (
                    "Can't assign p-field '{}'. P-field number has to bigger than 0."
                    .format(key0)
                )
                raise ValueError(message)

            pfields.append(pfield_key_to_function_mapping[key0])

            difference = number1 - number0
            if difference > 1:
                [pfields.append(lambda event: 0) for _ in range(difference - 1)]
                message = (
                    "Couldn't find any mapping for p-fields between '{}' and '{}'. "
                    .format(key0, key1)
                )
                message += "Assigned these p-fields to 0."
                warnings.warn(message)

        pfields.append(pfield_key_to_function_mapping[key1])
        return tuple(pfields)

    @staticmethod
    def _process_p_field_value(
        nth_p_field: int, p_field_value: typing.Any
    ) -> typing.Union[type(None), str]:
        """Makes sure pfield value is of correct type & adds quotation marks for str."""

        if isinstance(p_field_value, SupportedPFieldTypes.__args__):
            # silently adding quotation marks
            if isinstance(p_field_value, str):
                p_field_value = '"{}"'.format(p_field_value)

            else:
                p_field_value = "{}".format(p_field_value)

            return p_field_value

        else:
            message = (
                "Can't assign returned value '{}' of type '{}' to p-field {}.".format(
                    p_field_value, type(p_field_value), nth_p_field
                )
            )
            message += " Supported types for p-fields include '{}'. ".format(
                repr(SupportedPFieldTypes)
            )
            message += "Ignored p-field {}.".format(nth_p_field)
            warnings.warn(message)

    def _make_csound_score_lines_from_simple_event(
        self,
        simple_event: events.basic.SimpleEvent,
        absolute_entry_delay: parameters.durations.abc.DurationType,
        csound_score_lines: list,
    ) -> None:
        """Extract p-field data from simple event and write one Csound-Score line."""

        csound_score_line = "i"
        for nth_p_field, p_field_function in enumerate(self.pfields):
            # special case of absolute start time initialization
            if nth_p_field == 1 and p_field_function is None:
                csound_score_line += " {}".format(absolute_entry_delay)

            else:
                try:
                    p_field_value = p_field_function(simple_event)

                except AttributeError:
                    # if attribute couldn't be found, just make a rest
                    return

                p_field_value = CsoundScoreConverter._process_p_field_value(
                    nth_p_field, p_field_value
                )
                if p_field_value is not None:
                    csound_score_line += " {}".format(p_field_value)

        csound_score_lines.append(csound_score_line)

    def _make_csound_score_lines_from_sequential_event(
        self,
        sequential_event: events.basic.SequentialEvent,
        absolute_entry_delay: parameters.durations.abc.DurationType,
        csound_score_lines: list,
    ) -> None:
        for event_index, additional_delay in enumerate(sequential_event.absolute_times):
            self._make_csound_score_lines_from_event(
                sequential_event[event_index],
                absolute_entry_delay + additional_delay,
                csound_score_lines,
            )

    def _make_csound_score_lines_from_simultaneous_event(
        self,
        simultaneous_event: events.basic.SimultaneousEvent,
        absolute_entry_delay: parameters.durations.abc.DurationType,
        csound_score_lines: list,
    ) -> None:
        [
            self._make_csound_score_lines_from_event(
                event, absolute_entry_delay, csound_score_lines
            )
            for event in simultaneous_event
        ]

    def _make_csound_score_lines_from_event(
        self,
        event_to_convert: ConvertableEvent,
        absolute_entry_delay: parameters.durations.abc.DurationType,
        csound_score_lines: list,
    ):
        if isinstance(event_to_convert, events.basic.SequentialEvent):
            self._make_csound_score_lines_from_sequential_event(
                event_to_convert, absolute_entry_delay, csound_score_lines
            )

        elif isinstance(event_to_convert, events.basic.SimultaneousEvent,):
            self._make_csound_score_lines_from_simultaneous_event(
                event_to_convert, absolute_entry_delay, csound_score_lines
            )

        elif isinstance(event_to_convert, events.basic.SimpleEvent,):
            self._make_csound_score_lines_from_simple_event(
                event_to_convert, absolute_entry_delay, csound_score_lines
            )

        else:
            msg = (
                "Can't convert object '{}' of type '{}' to csound score lines.".format(
                    event_to_convert, type(event_to_convert)
                )
            )
            raise TypeError(msg)

    def convert(self, event_to_convert: ConvertableEvent) -> None:
        csound_score_lines = []
        # convert events to strings (where each string represents one csound score line)
        self._make_csound_score_lines_from_event(
            event_to_convert, 0, csound_score_lines
        )
        # write csound score lines to file
        with open(self.path, "w") as f:
            f.write("\n".join(csound_score_lines))
