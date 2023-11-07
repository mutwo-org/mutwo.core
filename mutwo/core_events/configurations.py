"""Configurations which are shared for all event classes in :mod:`mutwo.core_events`."""

import fractions
import functools
import typing

try:
    import quicktions
except ImportError:
    quicktions = None


def _add_quicktions(type_tuple: tuple[typing.Type, ...]) -> tuple[typing.Type, ...]:
    if quicktions:
        type_tuple += (quicktions.Fraction,)
    return type_tuple


# We can't set core_converters.UnknownObjectToObject
# directly because it would raise a circular import error.
@functools.cache
def __unknown_object_to_duration():
    import typing

    from mutwo import core_converters
    from mutwo import core_parameters

    def raise_parse_error(value: typing.Any):
        raise NotImplementedError(f"Can't parse '{value}' to a duration object!")

    def string_to_duration(string: str):
        if "." in string:
            f = float
        elif "/" in string:
            if quicktions:
                f = quicktions.Fraction
            else:
                f = fractions.Fraction
        else:
            f = int
        try:
            v = f(string)
        except ValueError:
            raise_parse_error(string)
        return UNKNOWN_OBJECT_TO_DURATION(v)

    return core_converters.UnknownObjectToObject[core_parameters.abc.Duration](
        (
            (
                _add_quicktions((float, int, fractions.Fraction)),
                core_parameters.DirectDuration,
            ),
            ((str,), string_to_duration),
        )
    )


# We don't define the function with `def UNKNOWN_OBJECT_TO_DURATION`
# because this is and should look like a global variable and not like
# a function.
UNKNOWN_OBJECT_TO_DURATION = lambda o: __unknown_object_to_duration()(o)
"""Global definition of callable to parse objects to :class:`mutwo.core_parameters.abc.Duration`.

This function is used in almost all objects which inherit from
:class:`mutwo.core_events.abc.Event`. It implements syntactic sugar
so that users can parse buildin types (or other objects) to mutwo callables
which expect :class:`mutwo.core_parameters.abc.Duration` objects.

This global variable is the reason why the following
code prints a :class:`mutwo.core_parameters.DirectDuration`:

    >>> from mutwo import core_events
    >>> simple_event = core_events.SimpleEvent(duration=10)
    >>> simple_event.duration
    DirectDuration(10)

Without this function...

    1. It wouldn't be certain that `duration` returns an instance
    of :class:`mutwo.core_parameters.abc.Duration`.

    2. Or the code would raise a ``TypeError`` and users would be forced
    to write:

        >>> core_events.SimpleEvent(core_parameters.DirectDuration(10))

Because the syntactic sugar partially violates the Python Zen
"Explicit is better than implicit" this function is publicly defined
in the `configurations` module (and not in private class methods),
so that users are encouraged to override the variable if desired.
"""


# Avoid circular import problem
@functools.cache
def __simpleEvent():
    return __import__("mutwo.core_events").core_events.SimpleEvent


DEFAULT_DURATION_TO_WHITE_SPACE = lambda duration: __simpleEvent()(duration)
"""Default conversion for parameter `duration_to_white_space` in
:func:`mutwo.core_events.abc.ComplexEvent.extend_until`. This simply
returns a :class:`mutwo.core_events.SimpleEvent` with the given
duration."""


# We can't set core_converters.UnknownObjectToObject
# directly because it would raise a circular import error.
@functools.cache
def __unknown_object_to_tempo_point():
    from mutwo import core_converters
    from mutwo import core_parameters

    type_tuple = _add_quicktions((float, int, fractions.Fraction))

    return core_converters.UnknownObjectToObject[core_parameters.abc.TempoPoint](
        ((type_tuple, core_parameters.DirectTempoPoint),)
    )


# We don't define the function with `def UNKNOWN_OBJECT_TO_DURATION`
# because this is and should look like a global variable and not like
# a function.
UNKNOWN_OBJECT_TO_TEMPO_POINT = lambda o: __unknown_object_to_tempo_point()(o)
"""Global definition of callable to parse objects to :class:`mutwo.core_parameters.abc.TempoPoint`.

It implements syntactic sugar so that users can parse buildin types
(or other objects) to mutwo callables which expect
:class:`mutwo.core_parameters.abc.TempoPoint` objects.

This global variable is the reason why the following
code prints a :class:`mutwo.core_parameters.DirectTempoPoint`:

    >>> from mutwo import core_events
    >>> t = core_events.TempoEvent(tempo_point=60, duration=1)
    >>> t.tempo_point
    DirectTempoPoint(BPM = 60, reference = 1)

Without this function...

    1. It wouldn't be certain that `tempo_point` returns an instance
    of :class:`mutwo.core_parameters.abc.TempoPoint`.

    2. Or the code would raise a ``TypeError`` and users would be forced
    to write:

        >>> core_events.TempoEvent(tempo_point=core_parameters.DirectTempoPoint(60), duration=1)

Because the syntactic sugar partially violates the Python Zen
"Explicit is better than implicit" this function is publicly defined
in the `configurations` module (and not in private class methods),
so that users are encouraged to override the variable if desired.
"""


# Configure envelopes submodule

DEFAULT_TEMPO_ENVELOPE_PARAMETER_NAME = "tempo_point"
"""Default property parameter name for events in
:class:`mutwo.core_events.TempoEnvelope`."""


# Avoid circular import problem
@functools.cache
def __event_to_parameter():
    return __import__("mutwo.core_converters").core_converters.SimpleEventToAttribute(
        "value", 0
    )


def _event_to_parameter(e):
    return __event_to_parameter()(e)


DEFAULT_EVENT_TO_PARAMETER = _event_to_parameter
"""Default value for `event_to_parameter` argument
of :class:`mutwo.core_events.Envelope`."""


# Avoid circular import problem
@functools.cache
def __event_to_curve_shape():
    return __import__("mutwo.core_converters").core_converters.SimpleEventToAttribute(
        "curve_shape", 0
    )


def _event_to_curve_shape(e):
    return __event_to_curve_shape()(e)


DEFAULT_EVENT_TO_CURVE_SHAPE = _event_to_curve_shape
"""Default value for `event_to_curve_shape` argument
of :class:`mutwo.core_events.Envelope`."""


def __parameter_to_value(p):
    return p


DEFAULT_PARAMETER_TO_VALUE = __parameter_to_value
"""Default value for `parameter_to_value` argument
of :class:`mutwo.core_events.Envelope`."""


def __value_to_parameter(p):
    return p


DEFAULT_VALUE_TO_PARAMETER = __value_to_parameter
"""Default value for `value_to_parameter` argument
of :class:`mutwo.core_events.Envelope`."""


def __apply_parameter_on_event(e, p):
    e.value = p


DEFAULT_APPLY_PARAMETER_ON_EVENT = __apply_parameter_on_event
"""Default value for `apply_parameter_on_event` argument
of :class:`mutwo.core_events.Envelope`."""


def __apply_curve_shape_on_event(e, p):
    e.curve_shape = p


DEFAULT_APPLY_CURVE_SHAPE_ON_EVENT = __apply_curve_shape_on_event
"""Default value for `apply_curve_shape` argument
of :class:`mutwo.core_events.Envelope`."""


def __default_event_class(*args, **kwargs):
    return __simpleEvent()(*args, **kwargs)


DEFAULT_DEFAULT_EVENT_CLASS = __default_event_class
"""Default value for `default_event_class` argument
of :class:`mutwo.core_events.Envelope`."""


def __initialise_default_event_class(cls, duration):
    return cls(duration)


DEFAULT_INITIALISE_DEFAULT_EVENT_CLASS = __initialise_default_event_class
"""Default value for `initialise_default_event_class` argument
of :class:`mutwo.core_events.Envelope`."""


del functools, typing
