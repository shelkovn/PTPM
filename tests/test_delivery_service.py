import unittest
from src.delivery_service import calculate_delivery_cost

class test_calculate_delivery_cost(unittest.TestCase):

    def test_invalid_values(self):
        expected = (-1, "0000-00-00")
        result = calculate_delivery_cost("aaa", 1, "обычный", False)
        self.assertEqual(expected, result)

    def test_excess_weight(self):
        expected = (-1, "0000-00-00")
        result = calculate_delivery_cost(100, 1, "обычный", False)
        self.assertEqual(expected, result)

    def test_underweight(self):
        expected = (-1, "0000-00-00")
        result = calculate_delivery_cost(0, 1, "обычный", False)
        self.assertEqual(expected, result)

    def test_short_distance(self):
        expected = (-1, "0000-00-00")
        result = calculate_delivery_cost(50, 0.1, "обычный", False)
        self.assertEqual(expected, result)

    def test_long_distance(self):
        expected = (-1, "0000-00-00")
        result = calculate_delivery_cost(50, 10000, "обычный", False)
        self.assertEqual(expected, result)

    def test_invalid_package_type(self):
        expected = (-1, "0000-00-00")
        result = calculate_delivery_cost(50, 10000, "sdasadsa", False)
        self.assertEqual(expected, result)

    def test_normal_parcel(self):
        distance = 20
        weight = 5
        expected = (200+distance*5, "2026-09-04")
        result = calculate_delivery_cost(weight, distance, "обычный", False)
        self.assertEqual(expected, result)

    def test_fragile_parcel(self):
        distance = 20
        weight = 5
        expected = (200+distance*5+300, "2026-09-04")
        result = calculate_delivery_cost(weight, distance, "хрупкий", False)
        self.assertEqual(expected, result)

    def test_dangerous_parcel(self):
        distance = 20
        weight = 5
        expected = (200+distance*5+1000, "2026-09-04")
        result = calculate_delivery_cost(weight, distance, "опасный", False)
        self.assertEqual(expected, result)

    def test_heavier_parcel(self):
        distance = 20
        weight = 10
        expected = ((200+distance*5)*1.2, "2026-09-04")
        result = calculate_delivery_cost(weight, distance, "обычный", False)
        self.assertEqual(expected, result)

    def test_extra_heavy_parcel(self):
        distance = 20
        weight = 50
        expected = ((200+distance*5)*1.5, "2026-09-04")
        result = calculate_delivery_cost(weight, distance, "обычный", False)
        self.assertEqual(expected, result)

    def test_express_parcel(self):
        distance = 1000
        weight = 5
        expected = (200+distance*5*2, "2026-09-04")
        result = calculate_delivery_cost(weight, distance, "обычный", True)
        self.assertEqual(expected, result)

    def test_rounding_delivery_date(self):
        distance = 750
        weight = 5
        expected = (200+distance*5, "2026-09-05")
        result = calculate_delivery_cost(weight, distance, "обычный", False)
        self.assertEqual(expected, result)

    def test_zero_day_delivery(self):
        distance = 5000
        weight = 5
        expected = (200+distance*5*2, "2026-09-04")
        result = calculate_delivery_cost(weight, distance, "обычный", True)
        self.assertEqual(expected, result)