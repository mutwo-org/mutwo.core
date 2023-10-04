"""This module contains performance tests.

Most of these tests ensure that there new patches don't introduce any performance regressions
"""

import random
import time
import unittest

from mutwo import core_events

sim = core_events.SimultaneousEvent
seq = core_events.SequentialEvent
s = core_events.SimpleEvent


def t(duration: float, try_count: int = 2):
    return lambda function: lambda self: self._t(function, duration, try_count)


class PerformanceTest(unittest.TestCase):
    def _t(self, function, duration: float, try_count: int = 2):
        def profile():
            n = time.time()
            function(self)
            return time.time() - n

        # Because it's indeterministic if the test succeeds we allow multiple
        # tries.
        for _ in range(try_count):
            delta = profile()
            if delta < duration:
                if delta * 1.5 < duration:
                    self.fail(
                        "The real duration is MUCH smaller than the "
                        f"expected duration\nreal duration = {delta}\n"
                        f"expected duration = {duration}"
                    )
                else:
                    self.assertGreater(duration, delta)
                return
            # The delta is too big, just let the test fail
            elif delta - duration > 0.5:
                break

        self.assertGreater(duration, delta)

    def setUp(self):
        random.seed(100)

    @t(0.065)
    def test_SequentialEvent_split_at(self):
        e = seq([s(random.uniform(1, 3)) for _ in range(1000)])
        duration = e.duration.duration_in_floats
        split_time_list = sorted([random.uniform(0, duration) for _ in range(100)])
        e.split_at(*split_time_list)

    @t(1.3)
    def test_SimultaneousEvent_split_at(self):
        e = sim([s(random.uniform(1, 3)) for _ in range(200)])
        duration = e.duration.duration_in_floats
        split_time_list = sorted([random.uniform(0, duration) for _ in range(50)])
        e.split_at(*split_time_list)

    @t(1.45)
    def test_metrize(self):
        e = sim(
            [seq([s(random.uniform(0.9, 1.2)) for _ in range(50)]) for _ in range(3)]
        )
        e.tempo_envelope = core_events.TempoEnvelope(
            [[i, 60] if i % 2 == 0 else [i, 50] for i in range(20)]
        )
        e.metrize()
