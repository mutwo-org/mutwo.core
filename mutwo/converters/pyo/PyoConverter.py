import pyo

from mutwo import converters
from mutwo import events


class PyoConverter(converters.abc.InPythonConverter):
    def __init__(self):
        pass

    def convert(self, event_to_convert: events.abc.Event) -> pyo.Events:
        pass
