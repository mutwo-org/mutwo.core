import dataclasses
import unittest

from mutwo.core.parameters import playing_indicators


class PlayingIndicatorCollectionTest(unittest.TestCase):
    def setUp(self):
        self.playing_indicator_collection = (
            playing_indicators.PlayingIndicatorCollection()
        )

    def test_frozen_attribute(self):
        def override_frozen_attribute():
            self.playing_indicator_collection.articulation = "This will raise an error."

        self.assertRaises(dataclasses.FrozenInstanceError, override_frozen_attribute)

    def test_syntactic_sugar_setter(self):
        # Normal setting of explicit playing indicators
        self.playing_indicator_collection.tie.is_active = False
        self.assertEqual(self.playing_indicator_collection.tie.is_active, False)

        # Syntactic sugar for setting explicit playing indicators
        self.playing_indicator_collection.tie = True
        self.assertEqual(self.playing_indicator_collection.tie.is_active, True)

        self.playing_indicator_collection.tie.is_active = False
