import unittest
from src.my_project import calculate_triangle

class test_triangles_app(unittest.TestCase):

    def test_normal(self):
        result = calculate_triangle("3", "4", "5")
        expected = ("разносторонний", [(12, 0), (88, 0), (88, 100)])
        self.assertEqual(result, expected)