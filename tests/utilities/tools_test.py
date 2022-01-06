import unittest

from mutwo.utilities import tools

from mutwo.parameters import pitches


class ToolsTest(unittest.TestCase):
    def test_scale_out_of_range(self):
        self.assertRaises(ValueError, tools.scale, 2, 0, 1, 1, 2)

    def test_scale_easy(self):
        result = tools.scale(0.5, 0, 1, 1, 2)
        self.assertEqual(result, 1.5)

    def test_scale_negative(self):
        result = tools.scale(0, -1, 1, 1, 2)
        self.assertEqual(result, 1.5)

    def test_scale_sequence_to_sum(self):
        result = tools.scale_sequence_to_sum([1, 3, 2], 3)
        self.assertEqual(result, [0.5, 1.5, 1])

    def test_accumulate_from_value(self):
        result = tuple(tools.accumulate_from_n((1, 2, 3), 6))
        self.assertEqual(result, (6, 7, 9, 12))

    def test_accumulate_from_zero(self):
        result = tuple(tools.accumulate_from_zero((1, 2, 3)))
        self.assertEqual(result, (0, 1, 3, 6))

    def test_insert_next_to_positive(self):
        result = [1, 2, 3]
        tools.insert_next_to(result, 2, 1, 4)
        self.assertEqual(result, [1, 2, 4, 3])

    def test_insert_next_to_zero(self):
        result = [1, 2, 3]
        tools.insert_next_to(result, 2, 0, 4)
        self.assertEqual(result, [1, 4, 3])

    def test_insert_next_to_negative(self):
        result = [1, 2, 3]
        tools.insert_next_to(result, 2, -1, 4)
        self.assertEqual(result, [1, 4, 2, 3])

    def test_find_closest_index_before(self):
        data = (1, 2, 3, 4, 5)
        self.assertEqual(tools.find_closest_index(-100, data), 0)

    def test_find_closest_index_after(self):
        data = (1, 2, 3, 4, 5)
        self.assertEqual(tools.find_closest_index(100, data), 4)

    def test_find_closest_index_in_between(self):
        data = (1, 2, 3, 4, 5)
        self.assertEqual(tools.find_closest_index(2.4, data), 1)

    def test_find_closest_index_in_unsorted_iterable(self):
        data = (4, 1, 2, 3, 100, 5)
        self.assertEqual(tools.find_closest_index(102, data), 4)

    def test_find_closest_item(self):
        data = (100, 200, 300)
        self.assertEqual(tools.find_closest_item(1000, data), 300)

    def test_uniqify(self):
        data0 = (100, 200, 300, 300, 100)
        expected_result0 = (100, 200, 300)
        unique0 = tools.uniqify_sequence(data0)

        data1 = (9, 9, 4, 2, 9, 5, 2)
        expected_result1 = (2, 4, 5, 9)
        unique1 = tools.uniqify_sequence(data1)

        # test for non hashable items
        data2 = [[1, 2], [100], [3, 2], [100], [3, 2], [3, 3]]
        expected_result2 = [[1, 2], [3, 2], [3, 3], [100]]
        unique2 = tools.uniqify_sequence(data2, sort_key=lambda iterable: sum(iterable))

        # test for mutwo objects
        data3 = [
            pitches.JustIntonationPitch(frequency_ratio)
            for frequency_ratio in "6/5 3/2 1/1 3/2 6/5 5/4".split(" ")
        ]
        expected_result3 = [
            pitches.JustIntonationPitch(frequency_ratio)
            for frequency_ratio in "1/1 6/5 5/4 3/2".split(" ")
        ]
        unique3 = tools.uniqify_sequence(
            data3,
            sort_key=lambda just_intonation_pitch: just_intonation_pitch.frequency,
        )

        self.assertEqual(expected_result0, unique0)
        self.assertEqual(expected_result1, unique1)
        self.assertEqual(expected_result2, unique2)
        self.assertEqual(expected_result3, unique3)

        # test if type preserving
        self.assertEqual(type(expected_result0), type(unique0))
        self.assertEqual(type(expected_result2), type(unique2))

    def test_cyclic_permutations(self):
        tuple_to_permute = (1, 2, 3)
        expected_permutations = ((1, 2, 3), (2, 3, 1), (3, 1, 2))

        permutation_generator = tools.cyclic_permutations(tuple_to_permute)
        for expected_permutation in expected_permutations:
            self.assertEqual(next(permutation_generator), expected_permutation)

    def test_camel_case_to_snake_case(self):
        self.assertEqual(tools.camel_case_to_snake_case("MyClassName"), "my_class_name")
        self.assertEqual(
            tools.camel_case_to_snake_case("MySecondClassName"), "my_second_class_name"
        )

    def test_get_nested_item_from_index_sequence(self):
        nested_sequence = (1, 2, (4, (5, 1), (9, (3,))))
        self.assertEqual(
            tools.get_nested_item_from_index_sequence((2, 2, 0), nested_sequence), 9
        )
        self.assertEqual(
            tools.get_nested_item_from_index_sequence((2, 2, 0), nested_sequence),
            nested_sequence[2][2][0],
        )

    def test_set_nested_item_from_index_sequence(self):
        nested_sequence = [1, 2, [4, [5, 1], [9, [3]]]]
        tools.set_nested_item_from_index_sequence((2, 2, 0), nested_sequence, 100)
        self.assertEqual(nested_sequence[2][2][0], 100)

    def test_find_numbers_which_sums_up_to(self):
        self.assertEqual(
            tools.find_numbers_which_sums_up_to(3), ((3,), (1, 2), (1, 1, 1))
        )
        self.assertEqual(
            tools.find_numbers_which_sums_up_to(5),
            ((5,), (1, 4), (2, 3), (1, 1, 3), (1, 2, 2), (1, 1, 1, 2), (1, 1, 1, 1, 1)),
        )
        # with custom argument for 'numbers_to_choose_from'
        self.assertEqual(
            tools.find_numbers_which_sums_up_to(6, (2, 3)),
            ((3, 3), (2, 2, 2)),
        )
        # with custom argument for 'numbers_to_choose_from' and 'n_items_to_sum_up'
        self.assertEqual(
            tools.find_numbers_which_sums_up_to(12, (2, 3), (4,)),
            ((3, 3, 3, 3),),
        )


if __name__ == "__main__":
    unittest.main()
