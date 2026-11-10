import unittest

import schedule


class ScheduleTests(unittest.TestCase):
    def test_parse_seconds(self):
        self.assertEqual(schedule.parse_duration("45s"), 45)

    def test_parse_hours(self):
        self.assertEqual(schedule.parse_duration("2h"), 7200)

    def test_parse_mixed(self):
        self.assertEqual(schedule.parse_duration("1h30m"), 5400)

    def test_merge_disjoint(self):
        self.assertEqual(schedule.merge_ranges([(4, 5), (1, 2)]), [(1, 2), (4, 5)])

    def test_merge_overlapping(self):
        self.assertEqual(schedule.merge_ranges([(1, 4), (2, 6)]), [(1, 6)])

    def test_merge_touching(self):
        self.assertEqual(schedule.merge_ranges([(1, 3), (3, 5)]), [(1, 5)])

    def test_window_sums(self):
        self.assertEqual(schedule.window_sums([1, 2, 3, 4], 2), [3, 5, 7])

    def test_window_larger_than_input(self):
        self.assertEqual(schedule.window_sums([1], 2), [])


if __name__ == "__main__":
    unittest.main()
