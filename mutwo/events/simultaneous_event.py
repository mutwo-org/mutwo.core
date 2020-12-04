from .complex_event import ComplexEvent


# TODO still interesting. is this a set?
class SimultaneousEvent(ComplexEvent):
    @property
    def duration(self):
        return max(tuple(element.duration for element in self))

    @duration.setter
    def duration(self, new_duration):
        for element in self:
            element.duration = new_duration