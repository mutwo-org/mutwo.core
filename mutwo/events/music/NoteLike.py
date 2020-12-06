from mutwo import events


class NoteLike(events.basic.SimpleEvent):
    def __init__(self, pitch_or_pitches, duration):
        super().__init__(duration)
