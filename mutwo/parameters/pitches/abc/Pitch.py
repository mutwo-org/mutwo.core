import abc


from mutwo import parameters


class Pitch(parameters.abc.Parameter):
    @property
    @abc.abstractmethod
    def frequency(self) -> float:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def midi_note(self) -> float:
        raise NotImplementedError
