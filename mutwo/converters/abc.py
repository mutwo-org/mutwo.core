"""Defining the public api for any converter class."""

import abc
import typing

from mutwo import events
from mutwo import parameters

__all__ = ("Converter", "EventConverter", "SymmetricalEventConverter")


class Converter(abc.ABC):
    """Abstract base class for all Converter classes.

    Converter classes are defined as classes that convert data between
    two different encodings. Their only public method (besides initialisation)
    should be a `convert` method that has exactly one argument (the data that
    should be converted).
    """

    @abc.abstractmethod
    def convert(self, event_or_parameter_or_file_to_convert: typing.Any) -> typing.Any:
        raise NotImplementedError


class EventConverter(Converter):
    """Abstract base class for Converter which handle mutwo events.

    This class helps building new classes which convert mutwo events
    with few general private methods (and without adding any new public
    method). Converting mutwo event often involves the same pattern:
    due to the nested structure of an Event, the converter has
    to iterate through the different layers until it reaches leaves
    (any class that inherits from :class:`mutwo.events.basic.SimpleEvent`).
    This common iteration process and the different time treatment
    between :class:`mutwo.events.basic.SequentialEvent` and
    :class:`mutwo.events.basic.SimultaneousEvent` are implemented in
    :class:`EventConverter`.  For writing a new EventConverter class,
    one only has to override the abstract method :func:`_convert_simple_event`
    and the abstract method :func:`convert` (where one will perhaps call
    :func:`_convert_event`.).

    **Example:**

    The following example defines a dummy class for demonstrating how
    to use EventConverter.

    >>> from mutwo.converters import abc
    >>> class DurationPrintConverter(abc.EventConverter):
    >>>     def _convert_simple_event(self, event_to_convert, absolute_entry_delay):
    >>>         return "{}: {}".format(absolute_entry_delay, event_to_convert.duration),
    >>>     def convert(self, event_to_convert):
    >>>         data_per_event = self._convert_event(event_to_convert, 0)
    >>>         [print(data) for data in data_per_event]
    >>> # now test with random event
    >>> import random
    >>> from mutwo.events import basic
    >>> random.seed(100)
    >>> random_event = basic.SimultaneousEvent(
    >>>     [
    >>>         basic.SequentialEvent(
    >>>             [
    >>>                 basic.SimpleEvent(random.uniform(0.5, 2))
    >>>                 for _ in range(random.randint(2, 5))
    >>>             ]
    >>>         )
    >>>         for _ in range(random.randint(1, 3))
    >>>     ]
    >>> )
    >>> DurationPrintConverter().convert(random_event)
    0: 1.182390506771032
    1.182390506771032: 1.6561757084885333
    2.8385662152595654: 1.558269840401042
    4.396836055660607: 1.5979384595498836
    5.994774515210491: 1.1502716523431056
    """

    @abc.abstractmethod
    def _convert_simple_event(
        self,
        event_to_convert: events.basic.SimpleEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> typing.Sequence[typing.Any]:
        """Convert instance of :class:`mutwo.events.basic.SimpleEvent`."""

        raise NotImplementedError

    def _convert_simultaneous_event(
        self,
        simultaneous_event: events.basic.SimultaneousEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> typing.Sequence[typing.Any]:
        """Convert instance of :class:`mutwo.events.basic.SimultaneousEvent`."""

        data_per_simple_event: typing.List[typing.Tuple[typing.Any]] = []

        for event in simultaneous_event:
            data_per_simple_event.extend(
                self._convert_event(event, absolute_entry_delay)
            )
        return tuple(data_per_simple_event)

    def _convert_sequential_event(
        self,
        sequential_event: events.basic.SequentialEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> typing.Sequence[typing.Any]:
        """Convert instance of :class:`mutwo.events.basic.SequentialEvent`."""

        data_per_simple_event: typing.List[typing.Tuple[typing.Any]] = []
        for event_start, event in zip(
            sequential_event.absolute_times, sequential_event
        ):
            data_per_simple_event.extend(
                self._convert_event(event, event_start + absolute_entry_delay)
            )
        return tuple(data_per_simple_event)

    def _convert_event(
        self,
        event_to_convert: events.abc.Event,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> typing.Any:
        """Convert :class:`mutwo.events.abc.Event` of unknown type.

        The method calls different subroutines depending on whether
        the passed event either are instances from:

            1. :class:`mutwo.events.basic.SimpleEvent` or
            2. :class:`mutwo.events.basic.SequentialEvent` or
            3. :class:`mutwo.events.basic.SimultaneousEvent`.
        """

        if isinstance(event_to_convert, events.basic.SequentialEvent):
            return self._convert_sequential_event(
                event_to_convert, absolute_entry_delay
            )

        elif isinstance(event_to_convert, events.basic.SimultaneousEvent,):
            return self._convert_simultaneous_event(
                event_to_convert, absolute_entry_delay
            )

        elif isinstance(event_to_convert, events.basic.SimpleEvent,):
            return self._convert_simple_event(event_to_convert, absolute_entry_delay)

        else:
            message = (
                "Can't convert object '{}' of type '{}' with EventConverter.".format(
                    event_to_convert, type(event_to_convert)
                )
            )

            message += " Supported types only include all inherited classes "
            message += "from '{}'.".format(events.abc.Event)
            raise TypeError(message)


class SymmetricalEventConverter(EventConverter):
    """Abstract base class for Converter which handle mutwo events.

    This converter is a more specified version of the :class:`EventConverter`.
    It helps for building converters which aim to return mutwo events.
    """

    def _convert_simple_event(
        self,
        event_to_convert: events.basic.SimpleEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> events.basic.SequentialEvent[events.basic.SimpleEvent]:
        """Convert instance of :class:`mutwo.events.basic.SimpleEvent`."""

        raise NotImplementedError

    def _convert_simultaneous_event(
        self,
        simultaneous_event: events.basic.SimultaneousEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> events.basic.SimultaneousEvent[events.abc.Event]:
        return events.basic.SimultaneousEvent(
            super()._convert_simultaneous_event(
                simultaneous_event, absolute_entry_delay
            )
        )

    def _convert_sequential_event(
        self,
        sequential_event: events.basic.SequentialEvent,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> events.basic.SequentialEvent[events.abc.Event]:
        return events.basic.SequentialEvent(
            super()._convert_sequential_event(sequential_event, absolute_entry_delay)
        )

    def _convert_event(
        self,
        event_to_convert: events.abc.Event,
        absolute_entry_delay: parameters.abc.DurationType,
    ) -> events.abc.ComplexEvent[events.abc.Event]:
        return super()._convert_event(event_to_convert, absolute_entry_delay)
