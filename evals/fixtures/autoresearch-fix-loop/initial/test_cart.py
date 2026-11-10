import unittest

import cart


class CartTests(unittest.TestCase):
    def test_subtotal_empty(self):
        self.assertEqual(cart.subtotal([]), 0)

    def test_subtotal_multiplies_quantity(self):
        self.assertEqual(cart.subtotal([(250, 2), (100, 1)]), 600)

    def test_discount_zero_cents(self):
        self.assertEqual(cart.apply_discount(0, 50), 0)

    def test_discount_ten_percent(self):
        self.assertEqual(cart.apply_discount(1000, 10), 900)

    def test_split_exact(self):
        self.assertEqual(cart.split_evenly(90, 3), [30, 30, 30])

    def test_split_keeps_remainder(self):
        self.assertEqual(cart.split_evenly(100, 3), [34, 33, 33])

    def test_format_money(self):
        self.assertEqual(cart.format_money(1905), "$19.05")

    def test_format_zero(self):
        self.assertEqual(cart.format_money(0), "$0.00")


if __name__ == "__main__":
    unittest.main()
