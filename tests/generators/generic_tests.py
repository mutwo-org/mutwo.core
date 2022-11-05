import unittest

from mutwo import core_events
from mutwo import core_generators


class DynamicChoiceTest(unittest.TestCase):
    def test_gamble_at(self):
        dynamic_choice = core_generators.DynamicChoice(
            [0, 1],
            [
                core_events.Envelope([(0, 0), (0.45, 0), (0.5, 0.5), (1, 1)]),
                core_events.Envelope([(0, 1), (0.5, 0.5), (0.6, 0), (1, 0)]),
            ],
        )
        for _ in range(1000):
            self.assertEqual(dynamic_choice.gamble_at(0), 1)
        for _ in range(1000):
            self.assertEqual(dynamic_choice.gamble_at(1), 0)
        center = [dynamic_choice.gamble_at(0.5) for _ in range(10000)]
        self.assertAlmostEqual(sum(center) / len(center), 0.5, places=2)

    def test_repr(self):
        dynamic_choice = core_generators.DynamicChoice(
            [0, 1],
            [
                core_events.Envelope([(0, 0), (1, 1)]),
                core_events.Envelope([(0, 1), (1, 0)]),
            ],
        )
        self.assertEqual(repr(dynamic_choice), "DynamicChoice([0, 1])")

    def test_items(self):
        value0, value1 = 0, 1
        envelope0, envelope1 = [
            core_events.Envelope([(0, 0), (1, 1)]),
            core_events.Envelope([(0, 1), (1, 0)]),
        ]
        dynamic_choice = core_generators.DynamicChoice(
            [value0, value1],
            [envelope0, envelope1],
        )
        self.assertEqual(
            dynamic_choice.items(), ((value0, envelope0), (value1, envelope1))
        )


if __name__ == "__main__":
    unittest.main()
