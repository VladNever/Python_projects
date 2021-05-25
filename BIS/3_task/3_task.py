import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from decimal import Decimal, ROUND_HALF_UP

PATH_TO_BROWSER_DRIVER = {
    'Chrome':'./drivers/chromedriver.exe'
}

class SearchPage:
    def __init__(self):
        self.driver = webdriver.Chrome(PATH_TO_BROWSER_DRIVER['Chrome'])

    @staticmethod
    def set_param_on_page(self, page, argument, accuracy):
        driver = self.driver
        driver.get(page)
        elem_argument = driver.find_element_by_id("argumentConv")
        elem_argument.send_keys(argument)
        elem_accuracy = Select(driver.find_element_by_id("sigfig"))
        elem_accuracy.select_by_value(accuracy)
        elem_format = Select(driver.find_element_by_id("format"))
        elem_format.select_by_value('0')
        driver.implicitly_wait(2)
        elem_result = driver.find_element_by_id("answer").text
        self.driver.close()
        return elem_result

    def conv_celsius_to_fahrenheit(self, argument, accuracy):
        page = "https://www.metric-conversions.org/temperature/celsius-to-fahrenheit.htm"
        elem_result = self.set_param_on_page(self, page, argument, accuracy)
        return elem_result

    def conv_meters_to_feet(self, argument, accuracy):
        page = "https://www.metric-conversions.org/length/meters-to-feet.htm"
        elem_result = self.set_param_on_page(self, page, argument, accuracy)
        return elem_result

    def conv_ounces_to_grams(self, argument, accuracy):
        page = "https://www.metric-conversions.org/weight/ounces-to-grams.htm"
        elem_result = self.set_param_on_page(self, page, argument, accuracy)
        return elem_result

class TestSearchPage(unittest.TestCase):
    def setUp(self):
        self.searchpage = SearchPage()
        self.argument = 1.232132
        self.accuracy = 4
        
    @staticmethod
    def define_rounding(self, testres):
        integ = len(str(testres).split('.')[0])
        rounding = self.accuracy - integ
        rounding = '1.' + '0' * rounding
        self.rounding = rounding

    @staticmethod
    def calculate_test_values(self, formula):
        test_result = formula
        self.define_rounding(self, test_result)
        test_result = Decimal(test_result).quantize(Decimal(self.rounding), ROUND_HALF_UP)
        test_result = str(test_result)
        return test_result

    def test_conv_cel_to_fahren(self):
        formula = self.argument * 1.80 +32.00
        test_result = self.calculate_test_values(self, formula)
        result = self.searchpage.conv_celsius_to_fahrenheit(str(self.argument), str(self.accuracy))
        self.assertIn(test_result, result)

    def test_conv_meters_to_feet(self):
        formula = self.argument * 3.2808
        test_result = self.calculate_test_values(self, formula)
        result = self.searchpage.conv_meters_to_feet(str(self.argument), str(self.accuracy))
        self.assertIn(test_result, result)

    def test_conv_ounces_to_grams(self):
        formula = self.argument / 0.035274
        test_result = self.calculate_test_values(self, formula)
        result = self.searchpage.conv_ounces_to_grams(str(self.argument), str(self.accuracy))
        self.assertIn(test_result, result)

 
if __name__ == "__main__":
  unittest.main()
