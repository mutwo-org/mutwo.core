# it is really important that Converter gets imported first
# otherwise you get a circular import
from . import abc
from .MidiFileConverter import MidiFileConverter
