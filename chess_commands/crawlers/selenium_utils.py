from selenium.common import StaleElementReferenceException


def text_not_empty_in_element(locator):
    def _predicate(driver):
        try:
            element_text = driver.find_element(*locator).get_attribute("innerText")
            if element_text and element_text.lower() != "starting position":
                return element_text
            else:
                return False
        except StaleElementReferenceException:
            return False

    return _predicate


def at_least_n_elements_with_text_except(locator, n, exceptions):
    def _predicate(driver):
        try:
            elements = driver.find_elements(*locator)
            if len(elements) >= n:
                for el in elements:
                    if not el.text or el.text in exceptions:
                        return False
                return elements
            else:
                return False
        except StaleElementReferenceException:
            return False

    return _predicate
