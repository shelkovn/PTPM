import unittest

from selenium import webdriver
from pages.calculator_page import CalculatorPage
from selenium.webdriver.chrome.options import Options

 #Для **Simple Calculator**: 
 # тесты на все арифметические операции (`+`, `-`, `*`, `/`, `**`),
 # граничные значения           ????
 # и обработку деления на ноль.

#2 / 3 = 0.6666666666666666
class CalculatorPageTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox() #chrome throws connection reset for some reason. dns? 
        self.driver.implicitly_wait(1) #if it cannot find the object, it will keep trying until 1s passes, then fails
        self.page_url = "https://www.globalsqa.com/angularJs-protractor/SimpleCalculator/"
        self.driver.get(self.page_url)
        self.page = CalculatorPage(self.driver)

    def tearDown(self):
        self.driver.quit()

#tests
    def test_add(self):
        a = 2
        b = 3
        op = "+"
        expected = f"{a} {op} {b} = {a + b}"
        self.assertEqual(self.page.calculate(a, b, op), expected)

    def test_sub(self):
        a = 2
        b = 3
        op = "-"
        expected = f"{a} {op} {b} = {a - b}"
        self.assertEqual(self.page.calculate(a, b, op), expected)

    def test_mult(self):
        a = 2
        b = 3
        op = "*"
        expected = f"{a} {op} {b} = {a * b}"
        self.assertEqual(self.page.calculate(a, b, op), expected)

    
    def test_div(self):
        a = 2
        b = 3
        op = "/"
        self.assertIn("= null", self.page.calculate(a, b, op))

    
    def test_div_zero(self):
        a = 2
        b = 0
        op = "/"
        self.assertIn("= null", self.page.calculate(a, b, op))
