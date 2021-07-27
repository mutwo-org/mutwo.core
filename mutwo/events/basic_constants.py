"""Constants which are shared for all event classes in :mod:`mutwo.events.basic`."""

ROUND_DURATION_TO_N_DIGITS = 10
"""Set floating point precision for the duration property of all
:class:`~mutwo.events.abc.Event` classes in the :mod:`mutwo.basic`
module.

When returning the duration property all mentioned events will
round their actual duration if the duration type is float. This
behaviour has been added with version 0.28.1 to avoid floating
point rounding errors which could occur in all duration related
methods of the different event classes (as it can happen in
for instance the :method:`mutwo.events.abc.ComplexEvent.squash_in`
method or the :method:`mutwo.events.abc.ComplexEvent.cut_off`
method)."""
