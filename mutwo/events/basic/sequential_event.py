from mutwo.events.abc.complex_event import ComplexEvent
from mutwo.utilities import tools


class SequentialEvent(ComplexEvent):
    @property
    def duration(self):
        return sum(element.duration for element in self)

    @duration.setter
    def duration(self, new_duration):
        new_durations = tools.scale_sum((s.duration for s in self), new_duration)
        # TODO this is shit. we want a more general approach manipulation attributes of sequences
        for nd, element in zip(new_durations, self):
            element.duration = nd

    # TODO we need inspect absolute timepoints or get absolute times (or both)
