import os
from tempfile import mkdtemp

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService


class Chrome:
    def __init__(self, headless=False, remote_url=None):
        self.remote_url = remote_url or os.getenv("CHROME_URL")
        self.driver = None
        self.headless = headless

    def get_driver(self, options):
        if self.remote_url:
            return webdriver.Remote(command_executor=self.remote_url, options=options)
        else:
            service = ChromeService(executable_path="/opt/chromedriver")
            return webdriver.Chrome(service=service, options=options)

    def connect_remote(self):
        options = webdriver.ChromeOptions()

        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Remote(
            command_executor=self.remote_url, options=options
        )
        return self.driver

    def connect_local(self):
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.binary_location = "/opt/chrome/chrome"
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--no-zygote")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.64 Safari/537.36"
        options.add_argument(f"user-agent={user_agent}")
        # options.add_argument("--disable-infobars")
        # options.add_argument("--disable-extensions")

        # This is to allow executing JS code that retrieves clipboard content.
        # See https://stackoverflow.com/questions/75712609/get-value-of-clipboard-from-a-selenium-grid-via-python
        # options.add_argument("--unsafely-allow-protected-media-identifier-for-domain")
        # options.add_experimental_option(
        #     "prefs",
        #     {
        #         "profile.content_settings.exceptions.clipboard": {
        #             "[*.]*,*": {
        #                 "last_modified": (time.time() * 1000),
        #                 "setting": 1,
        #             }
        #         }
        #     },
        # )

        if self.remote_url:
            self.driver = webdriver.Remote(
                command_executor=self.remote_url, options=options
            )
        else:
            service = ChromeService(executable_path="/opt/chromedriver")
            self.driver = webdriver.Chrome(service=service, options=options)
        return self.driver

    def connect(self):
        if self.remote_url:
            self.connect_remote()
        else:
            self.connect_local()

    def is_alive(self):
        try:
            self.driver.current_url
            return True
        except:
            return False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            try:
                import boto3
                from selenium.webdriver.common.by import By

                s3 = boto3.client("s3")
                el = self.driver.find_element(By.TAG_NAME, "body")
                el.screenshot("/tmp/crash.png")
                s3.upload_file(
                    "/tmp/crash.png",
                    os.environ["SCREENSHOT_BUCKET"],
                    "crash.png",
                    ExtraArgs=dict(ContentType="image/png"),
                )
                # print(self.driver.page_source)
            except Exception:
                self.driver.quit()
                return False
        self.driver.quit()
