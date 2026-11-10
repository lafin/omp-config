import unittest

import shipping


class ShippingTests(unittest.TestCase):
    def test_local_light(self):
        self.assertEqual(shipping.shipping_cost("local", 0.5), 5)

    def test_national_mid(self):
        self.assertEqual(shipping.shipping_cost("national", 3), 13)

    def test_international_heavy(self):
        self.assertEqual(shipping.shipping_cost("international", 10), 33)

    def test_very_heavy(self):
        self.assertEqual(shipping.shipping_cost("national", 25), 30)

    def test_express(self):
        self.assertEqual(shipping.shipping_cost("local", 0.5, express=True), 7.5)

    def test_unknown_zone(self):
        with self.assertRaises(ValueError):
            shipping.shipping_cost("moon", 1)

    def test_non_positive_weight(self):
        with self.assertRaises(ValueError):
            shipping.shipping_cost("local", 0)


if __name__ == "__main__":
    unittest.main()
