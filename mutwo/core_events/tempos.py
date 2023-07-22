from mutwo import core_events

__all__ = ("TempoEvent",)


# XXX: Currently type hints are deactivated here, because otherwise we get
# problems with circular imports (because 'TempoEvent' is needed by envelopes
# and because envelopes are needed by parameters). Because this code is very
# short, it may not matter so much.
class TempoEvent(core_events.SimpleEvent):
    def __init__(self, tempo_point, *args, **kwargs):
        self.tempo_point = tempo_point
        super().__init__(*args, **kwargs)

    @property
    def tempo_point(self):
        return self._tempo_point

    @tempo_point.setter
    def tempo_point(self, tempo_point):
        self._tempo_point = core_events.configurations.UNKNOWN_OBJECT_TO_TEMPO_POINT(
            tempo_point
        )
