"""Defining the public API for any converter class."""

import abc
import typing

from mutwo import core_events
from mutwo import core_parameters

__all__ = ("Converter", "EventConverter", "SymmetricalEventConverter")


class Converter(abc.ABC):
    """Abstract base class for all Converter classes.

    Converter classes are defined as classes that convert data between
    two different encodings. Their only public method (besides initialisation)
    should be a `convert` method. The first argument of the convert method
    should be the data to convert.
    """

    @abc.abstractmethod
    def convert(
        self, event_or_parameter_or_file_to_convert: typing.Any, *args, **kwargs
    ) -> typing.Any:
        ...

    def __call__(self, *args, **kwargs) -> typing.Any:
        return self.convert(*args, **kwargs)


class EventConverter(Converter):
    """Abstract base class for Converter which handle mutwo events.

    This class helps building new classes which convert mutwo events
    with few general private methods (and without adding any new public
    method). Converting mutwo event often involves the same pattern:
    due to the nested structure of an Event, the converter has
    to iterate through the different layers until it reaches leaves
    (any class that inherits from :class:`mutwo.core_events.SimpleEvent`).
    This common iteration process and the different time treatment
    between :class:`mutwo.core_events.SequentialEvent` and
    :class:`mutwo.core_events.SimultaneousEvent` are implemented in
    :class:`EventConverter`.  For writing a new EventConverter class,
    one only has to override the abstract method :func:`_convert_simple_event`
    and the abstract method :func:`convert` (where one will perhaps call
    :func:`_convert_event`.).

    **Example:**

    The following example defines a dummy class for demonstrating how
    to use EventConverter.

    >>> from mutwo import core_converters
    >>> class DurationPrintConverter(core_converters.abc.EventConverter):
    ...     def _convert_simple_event(self, event_to_convert, absolute_entry_delay):
    ...         return "{}: {}".format(absolute_entry_delay, event_to_convert.duration),
    ...     def convert(self, event_to_convert):
    ...         data_per_event = self._convert_event(event_to_convert, 0)
    ...         [print(data) for data in data_per_event]
    >>> # now test with random event
    >>> import random
    >>> from mutwo import core_events
    >>> random.seed(100)
    >>> random_event = core_events.SimultaneousEvent(
    ...     [
    ...        core_events.SequentialEvent(
    ...             [
    ...                core_events.SimpleEvent(random.uniform(0.5, 2))
    ...                 for _ in range(random.randint(2, 5))
    ...             ]
    ...         )
    ...         for _ in range(random.randint(1, 3))
    ...     ]
    ... )
    >>> DurationPrintConverter().convert(random_event)
    DirectDuration(duration = 0): DirectDuration(duration = 332813340356277/281474976710656)
    DirectDuration(duration = 332813340356277/281474976710656): DirectDuration(duration = 3729376151804513/2251799813685248)
    DirectDuration(duration = 6391882874654729/2251799813685248): DirectDuration(duration = 7017823472572815/4503599627370496)
    DirectDuration(duration = 19801589221882273/4503599627370496): DirectDuration(duration = 449779690686865/281474976710656)
    DirectDuration(duration = 26998064272872113/4503599627370496): DirectDuration(duration = 5180362984867255/4503599627370496)
    """

    @abc.abstractmethod
    def _convert_simple_event(
        self,
        event_to_convert: core_events.SimpleEvent,
        absolute_entry_delay: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> typing.Sequence[typing.Any]:
        """Convert instance of :class:`mutwo.core_events.SimpleEvent`."""

    def _convert_simultaneous_event(
        self,
        simultaneous_event: core_events.SimultaneousEvent,
        absolute_entry_delay: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> typing.Sequence[typing.Any]:
        """Convert instance of :class:`mutwo.core_events.SimultaneousEvent`."""

        data_per_simple_event_list: list[tuple[typing.Any]] = []

        for event in simultaneous_event:
            data_per_simple_event_list.extend(
                self._convert_event(event, absolute_entry_delay, depth + 1)
            )
        return tuple(data_per_simple_event_list)

    def _convert_sequential_event(
        self,
        sequential_event: core_events.SequentialEvent,
        absolute_entry_delay: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> typing.Sequence[typing.Any]:
        """Convert instance of :class:`mutwo.core_events.SequentialEvent`."""

        data_per_simple_event_list: list[tuple[typing.Any]] = []
        for event_start, event in zip(
            sequential_event.absolute_time_tuple, sequential_event
        ):
            data_per_simple_event_list.extend(
                self._convert_event(
                    event, event_start + absolute_entry_delay, depth + 1
                )
            )
        return tuple(data_per_simple_event_list)

    def _convert_event(
        self,
        event_to_convert: core_events.abc.Event,
        absolute_entry_delay: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> typing.Any:
        """Convert :class:`mutwo.core_events.abc.Event` of unknown type.

        The method calls different subroutines depending on whether
        the passed event either are instances from:

            1. :class:`mutwo.core_events.SimpleEvent` or
            2. :class:`mutwo.core_events.SequentialEvent` or
            3. :class:`mutwo.core_events.SimultaneousEvent`.
        """

        absolute_entry_delay = core_events.configurations.UNKNOWN_OBJECT_TO_DURATION(
            absolute_entry_delay
        )

        if isinstance(event_to_convert, core_events.SequentialEvent):
            conversion_method = self._convert_sequential_event
        elif isinstance(
            event_to_convert,
            core_events.SimultaneousEvent,
        ):
            conversion_method = self._convert_simultaneous_event
        elif isinstance(
            event_to_convert,
            core_events.SimpleEvent,
        ):
            conversion_method = self._convert_simple_event
        else:
            raise TypeError(
                f"Can't convert object '{event_to_convert}' of type "
                f"'{type(event_to_convert)}' with EventConverter."
                " Supported types only include all inherited classes "
                f"from '{core_events.abc.Event}'."
            )

        try:
            return conversion_method(event_to_convert, absolute_entry_delay, depth)
        except TypeError:
            return conversion_method(event_to_convert, absolute_entry_delay)


class SymmetricalEventConverter(EventConverter):
    """Abstract base class for Converter which handle mutwo core_events.

    This converter is a more specified version of the :class:`EventConverter`.
    It helps for building converters which aim to return mutwo core_events.
    """

    @abc.abstractmethod
    def _convert_simple_event(
        self,
        event_to_convert: core_events.SimpleEvent,
        absolute_entry_delay: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> core_events.SimpleEvent:
        """Convert instance of :class:`mutwo.core_events.SimpleEvent`."""

    def _convert_simultaneous_event(
        self,
        simultaneous_event: core_events.SimultaneousEvent,
        absolute_entry_delay: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> core_events.SimultaneousEvent:
        """Convert instance of :class:`mutwo.core_events.SimultaneousEvent`."""

        converted_simultaneous_event: core_events.SimultaneousEvent = (
            simultaneous_event.empty_copy()
        )

        for event in simultaneous_event:
            converted_simultaneous_event.append(
                self._convert_event(event, absolute_entry_delay, depth + 1)
            )
        return converted_simultaneous_event

    def _convert_sequential_event(
        self,
        sequential_event: core_events.SequentialEvent,
        absolute_entry_delay: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> core_events.SequentialEvent:
        """Convert instance of :class:`mutwo.core_events.SequentialEvent`."""

        converted_sequential_event: core_events.SequentialEvent = (
            sequential_event.empty_copy()
        )
        for event_start, event in zip(
            sequential_event.absolute_time_tuple, sequential_event
        ):
            converted_sequential_event.append(
                self._convert_event(
                    event, event_start + absolute_entry_delay, depth + 1
                )
            )
        return converted_sequential_event

    def _convert_event(
        self,
        event_to_convert: core_events.abc.Event,
        absolute_entry_delay: core_parameters.abc.Duration | float | int,
        depth: int = 0,
    ) -> core_events.abc.ComplexEvent[core_events.abc.Event]:
        return super()._convert_event(event_to_convert, absolute_entry_delay, depth)
