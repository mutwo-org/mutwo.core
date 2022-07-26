"""Configurations which are shared for all parameter classes in :mod:`mutwo.core_parameters`."""

ROUND_DURATION_TO_N_DIGITS = 10
"""Set floating point precision for the `duration_in_floats` property of all
:class:`~mutwo.core_parameters.abc.Duration` classes in the :mod:`mutwo.core_parameters`
module.

When returning the `duration_in_floats` property all mentioned events will
round their actual duration if the duration type is float. This
behaviour has been added with version 0.28.1 to avoid floating
point rounding errors which could occur in all duration related
methods of the different event classes (as it can happen in
for instance the :func:`mutwo.core_events.abc.ComplexEvent.squash_in`
method or the :func:`mutwo.core_events.abc.Event.cut_off`
method)."""
