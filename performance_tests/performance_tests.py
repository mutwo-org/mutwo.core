"""This module contains performance tests.

Most of these tests ensure that there new patches don't introduce any performance regressions
"""

import random
import timeit
import unittest

from mutwo import core_events
from mutwo import core_parameters

cnc = core_events.Concurrence
cns = core_events.Consecution
chn = core_events.Chronon


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
    def test_Consecution_split_at(self):
        e = cns([chn(random.uniform(1, 3)) for _ in range(100)])
        duration = e.duration.beat_count
        split_time_list = sorted([random.uniform(0, duration) for _ in range(100)])
        e.split_at(*split_time_list)

    @t(0.15, 100)
    def test_Concurrence_split_at(self):
        e = cnc([chn(random.uniform(1, 3)) for _ in range(30)])
        duration = e.duration.beat_count
        split_time_list = sorted([random.uniform(0, duration) for _ in range(25)])
        e.split_at(*split_time_list)

    @t(0.0885, 100)
    def test_metrize(self):
        e = cnc(
            [cns([chn(random.uniform(0.9, 1.2)) for _ in range(20)]) for _ in range(3)]
        )
        e.tempo = core_parameters.FlexTempo(
            [[i, 60] if i % 2 == 0 else [i, 50] for i in range(5)]
        )
        e.metrize()

    @t(0.03, 100)
    def test_Concurrence_copy(self):
        e = cnc(
            [
                cns([chn(random.uniform(1, 3)).set_parameter("a", 10) for _ in range(30)])
                for c in range(100)
            ]
        )
        e.copy()
