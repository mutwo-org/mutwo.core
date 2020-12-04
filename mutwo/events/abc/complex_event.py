import abc
import typing

import mutwo.events.abc as events_abc


class ComplexEvent(events_abc.Event, list):
    """Event-Object, which might contain other Event-Objects."""

    def __init__(self, iterable: typing.Iterable[events_abc.Event]):
        list.__init__(iterable)
