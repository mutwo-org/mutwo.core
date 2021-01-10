"""This module adds time-based Event abstractions.

Event objects can be understood as the core objects
of the mutwo framework. They all own a "duration"
attribute (which can be any number). Further more complex
Event classes with more relevant attributes can be generated
through inheriting from basic classes. mutwo already offers
support for several more complex representations (for instance
mutwo.events.music.NoteLike).

The most basic classes are:
    - mutwo.events.basic.SimpleEvent
    - mutwo.events.basic.SequentialEvent
    - mutwo.events.basic.SimultaneousEvent
"""

from . import abc
from . import basic
from . import music
