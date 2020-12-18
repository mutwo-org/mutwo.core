import abc

# import mutwo.events.basic as events_basic
import mutwo.parameters.abc as parameters_abc


class ParameterWithEnvelope(parameters_abc.Parameter):
    @property
    @abc.abstractmethod
    # def envelope(self) -> events_basic.SequentialEvent:
    def envelope(self) -> tuple:
        raise NotImplementedError
