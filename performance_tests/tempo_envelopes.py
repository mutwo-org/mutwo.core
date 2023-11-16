import cProfile
import random

from mutwo import core_events


def t():
    e = core_events.Concurrence(
        [
            core_events.Consecution(
                [core_events.Chronon(random.uniform(0.9, 1.2)) for _ in range(100)]
            )
            for _ in range(3)
        ]
    )
    e.tempo_envelope = core_events.TempoEnvelope(
        [[i, 60] if i % 2 == 0 else [i, 50] for i in range(20)]
    )
    e.metrize()


cProfile.run(t.__code__, sort=2)
