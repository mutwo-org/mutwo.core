"""Configurations which are shared for all event classes in :mod:`mutwo.core_events`."""

import typing

try:
    import quicktions as fractions
except ImportError:
    import fractions

# XXX: We can't set core_converters.UnknownObjectToObject
# directly because it would raise a circular import error.
def __unknown_object_to_duration(unknown_object):
    from mutwo import core_converters
    from mutwo import core_parameters

    return core_converters.UnknownObjectToObject[core_parameters.abc.Duration](
        (((float, int, fractions.Fraction), core_parameters.DirectDuration),)
    )(unknown_object)


# XXX: We don't define the function with `def UNKNOWN_OBJECT_TO_DURATION`
# because this is and should look like a global variable and not like
# a function.
UNKNOWN_OBJECT_TO_DURATION = __unknown_object_to_duration
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

# Configure envelopes submodule

DEFAULT_PARAMETER_ATTRIBUTE_NAME = "value"
"""Default attribute name when fetching the parameter of an event"""

DEFAULT_CURVE_SHAPE_ATTRIBUTE_NAME = "curve_shape"
"""Default attribute name when fetching the curve shape of an event"""

del typing
