import unittest

import grades


class GradesTests(unittest.TestCase):
    def test_letters(self):
        self.assertEqual([grades.letter(s) for s in (95, 85, 75, 65, 10, 90, 60)], list("ABCDFAD"))

    def test_average(self):
        self.assertEqual(grades.average([50, 100]), 75)
        self.assertEqual(grades.average([]), 0)

    def test_highest(self):
        self.assertEqual(grades.highest([3, 9, 4]), 9)
        self.assertIsNone(grades.highest([]))

    def test_passing(self):
        self.assertEqual(grades.passing([59, 60, 99]), [60, 99])

    def test_pass_rate(self):
        self.assertEqual(grades.pass_rate([50, 70, 80, 10]), 0.5)
        self.assertEqual(grades.pass_rate([]), 0)

    def test_report(self):
        self.assertEqual(grades.report([40, 80]), {"average": 60, "highest": 80, "pass_rate": 0.5})
        self.assertEqual(grades.report([]), {"average": 0, "highest": None, "pass_rate": 0})


if __name__ == "__main__":
    unittest.main()
