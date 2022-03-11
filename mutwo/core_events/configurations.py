"""Configurations which are shared for all event classes in :mod:`mutwo.events.basic`."""

# Configure basic submodule

ROUND_DURATION_TO_N_DIGITS = 10
"""Set floating point precision for the duration property of all
:class:`~mutwo.events.abc.Event` classes in the :mod:`mutwo.basic`
module.

When returning the duration property all mentioned events will
round their actual duration if the duration type is float. This
behaviour has been added with version 0.28.1 to avoid floating
point rounding errors which could occur in all duration related
methods of the different event classes (as it can happen in
for instance the :func:`mutwo.events.abc.ComplexEvent.squash_in`
method or the :func:`mutwo.events.abc.Event.cut_off`
method)."""

# Configure envelopes submodule

DEFAULT_PARAMETER_ATTRIBUTE_NAME = "value"
"""Default attribute name when fetching the parameter of an event"""

DEFAULT_CURVE_SHAPE_ATTRIBUTE_NAME = "curve_shape"
"""Default attribute name when fetching the curve shape of an event"""
