from mutwo.events import abc
from mutwo.utilities import tools


class SequentialEvent(abc.ComplexEvent):
    @property
    def duration(self):
        return sum(event.duration for event in self)

    @duration.setter
    def duration(self, new_duration):
        new_durations = tools.scale_sum((event.duration for event in self), new_duration)
        # TODO this is shit. we want a more general approach manipulation attributes of sequences
        for new_duration, event in zip(new_durations, self):
            event.duration = new_duration

    # TODO we need inspect absolute timepoints or get absolute times (or both)
