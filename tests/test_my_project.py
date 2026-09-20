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

    def test_zeroes(self):
        result = calculate_triangle("0", "0", "0")
        expected = ("не треугольник", [(-1, -1)] * 3)
        self.assertEqual(result, expected)

    def test_negative_values(self):
        result = calculate_triangle("-10", "-1", "-10")
        expected = ("не треугольник", [(-1, -1)] * 3)
        self.assertEqual(result, expected)

    def test_isosceles(self):
        result = calculate_triangle("10", "1", "10")
        expected = ("равнобедренный", [(0, 45), (100, 45), (100, 55)])
        self.assertEqual(result, expected)

    def test_equilateral(self):
        result = calculate_triangle("10", "10", "10")
        expected = ("равносторонний", [(0, 7), (100, 7), (50, 93)])
        self.assertEqual(result, expected)

    def test_big_values(self):
        result = calculate_triangle("9223372036854775807000000000", "9223372000000000036854775807", "92000000023372036854775807")
        expected = ("разносторонний", [(0, 50), (100, 50), (0, 50)])
        self.assertEqual(result, expected)   #flattens to a line

    def test_small_values(self):
        result = calculate_triangle("0.0000000000000000000000000001", "0.0000000000000000000000000009", "0.00000000000000000000000000085")
        expected = ("разносторонний", [(69, 0), (82, 0), (18, 100)])
        self.assertEqual(result, expected)

    def test_isosceles_base_smaller(self):
        result = calculate_triangle("5", "5", "8")
        expected = ("равнобедренный", [(0, 13), (78, 13), (100, 88)])
        self.assertEqual(result, expected)

    def test_isosceles_base_larger(self):
        result = calculate_triangle("8", "5", "5")
        expected = ("равнобедренный", [(0, 31), (100, 31), (50, 69)])
        self.assertEqual(result, expected)

    def test_scalene_obtuse(self):
        result = calculate_triangle("7", "10", "5")
        expected = ("разносторонний", [(21, 24), (100, 24), (0, 76)])
        self.assertEqual(result, expected)

    def test_right_angle_scalene(self):
        result = calculate_triangle("6", "8", "10")
        expected = ("разносторонний", [(12, 0), (88, 0), (88, 100)])
        self.assertEqual(result, expected)

    def test_right_angle_isosceles(self):
        result = calculate_triangle("1", "1", "1.41421356")
        expected = ("равнобедренный", [(0, 0), (100, 0), (100, 100)])
        self.assertEqual(result, expected)

    def test_micro_equilateral(self):
        result = calculate_triangle("0.001", "0.001", "0.001")
        expected = ("равносторонний", [(0, 7), (100, 7), (50, 93)])
        self.assertEqual(result, expected)

    def test_macro_equilateral(self):
        result = calculate_triangle("100000", "100000", "100000")
        expected = ("равносторонний", [(0, 7), (100, 7), (50, 93)])
        self.assertEqual(result, expected)

    def test_scalene_acute(self):
        result = calculate_triangle("10", "20", "25")
        expected = ("разносторонний", [(7, 0), (60, 0), (93, 100)])
        self.assertEqual(result, expected)

    def test_all_strings_invalid(self):
        result = calculate_triangle("abc", "def", "ghi")
        expected = ("", [(-2, -2)] * 3)
        self.assertEqual(result, expected)

    def test_degenerate_flat_line(self):
        # Sum of two sides exactly equals the third side (a + b == c)
        result = calculate_triangle("10", "5", "5")
        expected = ("не треугольник", [(-1, -1)] * 3)
        self.assertEqual(result, expected)

    def test_mixed_negative_side(self):
        result = calculate_triangle("3", "4", "-5")
        expected = ("не треугольник", [(-1, -1)] * 3)
        self.assertEqual(result, expected)

    
    