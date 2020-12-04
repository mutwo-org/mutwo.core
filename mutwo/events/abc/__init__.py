# it is really important that Event gets imported before ComplexEvent, because ComplexEvent depends on Event
# otherwise you get a circular import
from .event import Event
from .complex_event import ComplexEvent
