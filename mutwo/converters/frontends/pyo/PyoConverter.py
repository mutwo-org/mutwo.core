import pyo

from mutwo.converters.frontends import abc as converters_frontends_abc
from mutwo import events

class PyoConverter(converters_frontends_abc.InPythonConverter):
    def __init__(self):
        pass

    def convert(self, event_to_convert: events.abc.Event) -> pyo.Events:
        pass
