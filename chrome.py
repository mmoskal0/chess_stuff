import os
import time

from selenium import webdriver


class Chrome:
    def __init__(self, url=None):
        self.url = url or os.getenv("CHROME_URL")
        self.driver = None

    def connect(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        # This is to allow executing JS code that retrieves clipboard content.
        # See https://stackoverflow.com/questions/75712609/get-value-of-clipboard-from-a-selenium-grid-via-python
        options.add_experimental_option(
            "prefs",
            {
                "profile.content_settings.exceptions.clipboard": {
                    "[*.]*,*": {
                        "last_modified": (time.time() * 1000),
                        "setting": 1,
                    }
                }
            },
        )
        self.driver = webdriver.Remote(command_executor=self.url, options=options)

        return self.driver

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()
