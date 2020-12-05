# it is really important that Event gets imported before ComplexEvent, because ComplexEvent depends on Event
# otherwise you get a circular import
from .Event import Event
from .ComplexEvent import ComplexEvent
