from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CalculatorPage():
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def _click(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def _type(self, locator, text, clear=True):
        element = self._find(locator)
        if clear:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        return self._find(locator).text

    def get_value(self, locator):
        """for inputs"""
        return self._find(locator).get_attribute("value")

    __A_INPUT = (By.CSS_SELECTOR, "input[ng-model='a']")
    __A_INCREMENT = (By.CSS_SELECTOR, "button[ng-click='inca()']")
    __A_DECREMENT = (By.CSS_SELECTOR, "button[ng-click='deca()']")
    __B_INPUT = (By.CSS_SELECTOR, "input[ng-model='b']")
    __B_INCREMENT = (By.CSS_SELECTOR, "button[ng-click='incb()']")
    __B_DECREMENT = (By.CSS_SELECTOR, "button[ng-click='decb()']")
    __OPERATION_SELECT = (By.CSS_SELECTOR, "select[ng-model='operation']")
    __RESULT_LABEL = (By.CSS_SELECTOR, ".result.ng-binding")

    def enter_a(self, value):
        self._type(self.__A_INPUT, str(value))

    def enter_b(self, value):
        self._type(self.__B_INPUT, str(value))

    def increase_a(self):
        self._click(self.__A_INCREMENT)

    def decrease_a(self):
        self._click(self.__A_DECREMENT)

    def increase_b(self):
        self._click(self.__B_INCREMENT)

    def decrease_b(self):
        self._click(self.__B_DECREMENT)

    def get_a(self) -> str:
        return self.get_value(self.__A_INPUT)

    def get_b(self) -> str:
            return self.get_value(self.__B_INPUT)

    def select_operation(self, operation_value: str):
        """
        operation_value: + | - | / | *
        """
        select_element = self._find(self.__OPERATION_SELECT)
        Select(select_element).select_by_value(operation_value)

    def get_result(self) -> str:
        return self.get_text(self.__RESULT_LABEL)

    def calculate(self, a, b, operation):
        self.enter_a(a)
        self.enter_b(b)
        self.select_operation(operation)
        return self.get_result()