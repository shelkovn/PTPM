import unittest
from Converter import Converter

class test_Converter(unittest.TestCase):

    def setUp(self):
        self.converter = Converter()

    def test_nonfloat(self):
        with self.assertRaisesRegex(ValueError, "not a float"):
            self.converter.do(1)

    def test_not_1_decimal(self):
        with self.assertRaisesRegex(ValueError, "not one decimal"):
            self.converter.do(1.001)

    #def test_not_1_decimal(self):
    #    with self.assertRaisesRegex(ValueError, "not one decimal"):
    #        self.converter.do(1.00)

    def test_below_1(self):
        expected = -2000
        result = self.converter.do(-310.1)
        self.assertEqual(expected, result)

    def test_border_1(self):
        expected = -2000
        result = self.converter.do(-30.5)
        self.assertEqual(expected, result)

    def test_below_2(self):
        x = -20.5
        expected = -25
        result = self.converter.do(x)
        self.assertEqual(expected, result)

    def test_border_2(self):
        with self.assertRaisesRegex(ValueError, "recieved zero"):
            self.converter.do(0.0)

    def test_below_3(self):
        x = 20.5
        expected = int(x)
        result = self.converter.do(x)
        self.assertEqual(expected, result)

    def test_border_3(self):
        x = 100.7
        expected = 1000
        result = self.converter.do(x)
        self.assertEqual(expected, result)

    def test_above_3(self):
        x = 11000.5
        expected = 1000
        result = self.converter.do(x)
        self.assertEqual(expected, result)
