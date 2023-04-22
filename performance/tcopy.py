import cProfile
import random

from mutwo import core_events

random.seed(100)


def t():
    s = core_events.SimultaneousEvent(
        [
            core_events.SequentialEvent(
                [core_events.SimpleEvent(random.uniform(1, 3)) for _ in range(1000)]
            )
            for _ in range(20)
        ]
    )
    s.copy()
    # s.destructive_copy()


# 6.4
cProfile.run(t.__code__, sort=2)
