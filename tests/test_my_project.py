import unittest
from src.my_project import calculate_triangle

class test_triangles_app(unittest.TestCase):

    def test_normal(self):
        result = calculate_triangle("3", "4", "5")
        expected = ("разносторонний", [(12, 0), (88, 0), (88, 100)])
        self.assertEqual(result, expected)

    def test_invalid_lengths(self):
        result = calculate_triangle("10", "1", "1")
        expected = ("не треугольник", [(-1, -1)] * 3)
        self.assertEqual(result, expected)

    #def test_exception(self):
    #    with self.assertRaises(ValueError):
    #        calculate_triangle("abc", "4", "5")

    def test_invalid_values(self):
        result = calculate_triangle("abc", "4", "5")
        expected = ("", [(-2, -2)] * 3)
        self.assertEqual(result, expected)

    