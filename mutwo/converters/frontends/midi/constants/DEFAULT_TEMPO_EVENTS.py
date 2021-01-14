from mutwo import events
from mutwo import parameters

DEFAULT_TEMPO_EVENTS = events.basic.SequentialEvent(
    [events.basic.EnvelopeEvent(1, parameters.tempos.TempoPoint(120, 1))]
)
