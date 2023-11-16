import cProfile
import random

from mutwo import core_events

random.seed(100)


def t():
    s = core_events.Consecution(
        [core_events.Chronon(random.uniform(1, 3)) for _ in range(200)]
    )
    duration = s.duration.duration_in_floats
    split_time_list = sorted([random.uniform(0, duration) for _ in range(70)])
    s.split_at(*split_time_list)
    # for t in split_time_list:
    #     s.split_at(t)


# 6.4
cProfile.run(t.__code__, sort=2)
