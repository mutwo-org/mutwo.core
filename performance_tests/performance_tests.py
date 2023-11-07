"""This module contains performance tests.

Most of these tests ensure that there new patches don't introduce any performance regressions
"""

import random
import timeit
import unittest

from mutwo import core_events

sim = core_events.SimultaneousEvent
seq = core_events.SequentialEvent
s = core_events.SimpleEvent


def t(duration: float, repetition_count: int = 100, raise_delta: bool = False):
    return lambda function: lambda self: self._t(
        function, duration, repetition_count, raise_delta
    )


class PerformanceTest(unittest.TestCase):
    def _t(
        self,
        function,
        duration: float,
        repetition_count: int = 100,
        raise_delta: bool = False,
    ):
        delta = (
            timeit.timeit(
                "function(self)",
                globals={"function": function, "self": self},
                number=repetition_count,
            )
            / repetition_count
        )
        self.assertGreater(duration, delta)
        if raise_delta:
            raise ValueError("duration", delta)

    def setUp(self):
        random.seed(100)

    @t(0.06, 200)
    def test_SequentialEvent_split_at(self):
        e = seq([s(random.uniform(1, 3)) for _ in range(100)])
        duration = e.duration.duration
        split_time_list = sorted([random.uniform(0, duration) for _ in range(100)])
        e.split_at(*split_time_list)

    @t(0.15, 100)
    def test_SimultaneousEvent_split_at(self):
        e = sim([s(random.uniform(1, 3)) for _ in range(30)])
        duration = e.duration.duration
        split_time_list = sorted([random.uniform(0, duration) for _ in range(25)])
        e.split_at(*split_time_list)

    @t(0.12, 100)
    def test_metrize(self):
        e = sim(
            [seq([s(random.uniform(0.9, 1.2)) for _ in range(20)]) for _ in range(3)]
        )
        e.tempo_envelope = core_events.TempoEnvelope(
            [[i, 60] if i % 2 == 0 else [i, 50] for i in range(5)]
        )
        e.metrize()
