from mutwo.parameters import pitches


class DirectPitch(pitches.abc.Pitch):
    """A simple pitch class that gets directly initialised by its frequency.

    May be used when a converter class needs a pitch object, but there is
    no need or desire for a complex abstraction of the respective pitch
    (that classes like JustIntonationPitch or WesternPitch offer).
    """

    def __init__(self, frequency: float):
        self._frequency = frequency

    @property
    def frequency(self) -> float:
        return self._frequency

    def __repr__(self) -> str:
        return "DirectPitch(frequency = {})".format(self.frequency)
