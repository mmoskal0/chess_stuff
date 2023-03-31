from datetime import datetime
import json
import os
from urllib.parse import urljoin

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class ChesscomCrawler:
    base_url = "https://chess.com/"

    def url(self, path):
        return urljoin(self.base_url, path)

    def login(self, driver):
        success = self.login_with_cookie(driver)
        if not success:
            return self.login_with_password(driver)
        return success

    def login_with_cookie(self, driver):
        driver.get(self.url("home"))
        cookie = self.load_cookie()
        if cookie:
            driver.add_cookie(cookie)
        return cookie

    def login_with_password(self, driver):
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")

        driver.get(self.url("login"))
        driver.find_element("id", "username").send_keys(username)
        driver.find_element("id", "password").send_keys(password)
        driver.find_element("id", "_remember_me").click()
        driver.find_element("id", "login").click()

        cookie = WebDriverWait(driver, timeout=10).until(
            lambda x: x.get_cookie("CHESSCOM_REMEMBERME")
        )
        if cookie:
            self.store_cookie(cookie)
        return cookie

    def store_cookie(self, cookie):
        with open("cookie.txt", "w") as file:
            file.write(json.dumps(cookie))

    def load_cookie(self):
        try:
            with open("cookie.txt", "r") as file:
                content = file.read()
                cookie = json.loads(content) if content else None
        except IOError:
            return None

        if not cookie or datetime.fromtimestamp(cookie["expiry"]) < datetime.now():
            return None
        return cookie

    def skip_trial(self, driver):
        try:
            skip_trial = driver.find_element(By.XPATH, "//button[text()='Skip Trial']")
            skip_trial.click()
        except NoSuchElementException:
            pass

    def read_clipboard(self, driver):
        clipboard_text = driver.execute_script("return navigator.clipboard.readText()")
        return clipboard_text

    def create_arena(self, driver, name):
        self.login(driver)
        self.skip_trial(driver)

        driver.get(self.url("play/online/tournaments#club-event"))

        new_arena_button = WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//button[./descendant::div[text()='New Arena']]")
            )
        )
        new_arena_button.click()

        name_input = driver.find_element(
            By.XPATH, "//div[@data-cy='club-event-name']/input"
        )
        name_input.send_keys(name)

        create_button = driver.find_element(
            By.XPATH, "//button[contains(text(),'Create')]"
        )
        create_button.click()

        WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, f"//div[text()='{name} Arena']")
            )
        )
        share_button = driver.find_element(
            By.XPATH, "//button[@aria-label='Copy Link']"
        )
        share_button.click()
        return self.read_clipboard(driver)
