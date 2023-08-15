from datetime import datetime, timezone
import json
import os
import time
from urllib.parse import urljoin

import requests
from selenium.common import (
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

from crawlers.selenium_utils import (
    text_not_empty_in_element,
    at_least_n_elements_with_text_except,
)

chess_uuids = {
    "annamaja": "160ee19e-830f-11e5-800a-000000000000",
    "hannahsayce": "fd91f7ea-7479-11e9-8e68-69b78e4292d1",
}


class ChesscomCrawler:
    base_url = "https://www.chess.com/"

    def __init__(self):
        self.bot_username = os.environ["BOT_USERNAME"]
        self.cookie_value = os.environ["CHESSCOM_REMEMBERME"]

    def url(self, path):
        return urljoin(self.base_url, path)

    @property
    def cookie(self):
        return {"CHESSCOM_REMEMBERME": self.cookie_value}

    def login(self, driver):
        success = self.login_with_cookie(driver)
        if not success:
            return self.login_with_password(driver)
        return success

    def login_with_cookie(self, driver):
        driver.get(self.url("home"))
        # if a cookie expires, it's easier to just replace it once a year
        next_year = int(time.time()) + 31536000

        cookie = {
            "domain": ".www.chess.com",
            "expiry": next_year,
            "httpOnly": True,
            "name": "CHESSCOM_REMEMBERME",
            "path": "/",
            "sameSite": "Lax",
            "secure": True,
            "value": self.cookie_value,
        }
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
        return cookie

    def get_uuid(self, username):
        global chess_uuids
        if username in chess_uuids:
            print("HIT CACHE FOR UUID")
            return chess_uuids[username]

        response = requests.get(f"https://www.chess.com/callback/user/popup/{username}")
        try:
            uuid = response.json()["uuid"]
            chess_uuids[username] = uuid
        except:
            uuid = None
        return uuid

    def get_game_url(self, game_id):
        return self.url(f"game/live/{game_id}")

    def get_user_activity(self, username):
        uuid = self.get_uuid(username)
        if not uuid:
            return False, "Invalid chess.com username"
        r = requests.get(
            f"https://www.chess.com/service/presence/watch/users?ids={uuid}",
            cookies=self.cookie,
            stream=True,
        )
        return r.iter_lines(decode_unicode=True)

    def get_activity_status(self, activity):
        status, game_id = None, None
        for record in activity:
            if record.startswith("data"):
                data = json.loads(record[5:])
                if data["status"] != "online":
                    status = "not online"
                    return status, game_id
                if data["activity"] != "playing":
                    status = "online but not playing"
                    return status, game_id
                game_id = data["activityContext"]["games"][0]["legacyId"]
                return status, game_id

    def skip_trial(self, driver):
        try:
            skip_trial = driver.find_element(By.XPATH, "//button[text()='Skip Trial']")
            skip_trial.click()
        except NoSuchElementException:
            pass

    def read_clipboard(self, driver):
        clipboard_text = driver.execute_script("return navigator.clipboard.readText()")
        return clipboard_text

    def upcoming_tournaments(self, club_id):
        r = requests.get(
            f"https://www.chess.com/callback/clubs/live/upcoming/{club_id}",
            cookies=self.cookie,
        ).json()
        arenas = r["arena"]
        tournaments = r["live_tournament"]
        return arenas, tournaments

    def current_tournaments(self, club_id):
        r = requests.get(
            f"https://www.chess.com/callback/clubs/live/current/{club_id}",
            cookies=self.cookie,
        ).json()
        arenas = r["arena"]
        tournaments = r["live_tournament"]
        return arenas, tournaments

    def last_move(self, driver):
        move = driver.find_elements(
            By.XPATH, "//div[@data-ply and contains(@class, 'node')]"
        )[-1]
        try:
            figure = move.find_element(By.TAG_NAME, "span").get_attribute(
                "data-figurine"
            )
        except NoSuchElementException:
            figure = ""

        return f"{figure}{move.text}"

    def _ensure_url(self, driver, desired_url):
        reload = False
        current_url = driver.current_url
        while current_url != desired_url:
            reload = True
            watch_close = WebDriverWait(driver, 3).until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, "//div[@data-tab='game']/button")
                )
            )
            watch_close.click()
            time.sleep(0.2)
            current_url = driver.current_url
        return reload

    def _get_eval(self, driver):
        score = WebDriverWait(driver, 10).until(
            text_not_empty_in_element((By.CLASS_NAME, "evaluation-bar-score"))
        )
        last_move = self.last_move(driver)
        return score, last_move

    def eval(self, driver, game_id, screenshot=False):
        game_url = self.get_game_url(game_id)
        driver.get(game_url)
        result = self._get_eval(driver)
        reload = self._ensure_url(driver, game_url)
        if reload:
            result = self._get_eval(driver)
        if screenshot:
            self.screenshot(driver)

        return result

    def players(self, driver, game_id):
        game_url = self.get_game_url(game_id)
        driver.get(game_url)
        users = WebDriverWait(driver, 10).until(
            at_least_n_elements_with_text_except(
                (By.CLASS_NAME, "user-username-component"),
                2,
                (self.bot_username, "Opponent"),
            )
        )
        reload = self._ensure_url(driver, game_url)
        if reload:
            users = WebDriverWait(driver, 10).until(
                at_least_n_elements_with_text_except(
                    (By.CLASS_NAME, "user-username-component"),
                    2,
                    (self.bot_username, "Opponent"),
                )
            )
        user1, user2 = users[0].text, users[1].text
        return user1, user2

    def get_member_url(self, username):
        return self.url(f"member/{username}")

    def opening(self, driver, game_id, screenshot=False):
        game_url = self.get_game_url(game_id)
        driver.get(game_url)
        opening = WebDriverWait(driver, 25).until(
            text_not_empty_in_element((By.CLASS_NAME, "eco-opening-name"))
        )
        reload = self._ensure_url(driver, game_url)
        if reload:
            opening = WebDriverWait(driver, 10).until(
                text_not_empty_in_element((By.CLASS_NAME, "eco-opening-name"))
            )
        if screenshot:
            self.screenshot(driver)
        return opening

    def type_slow(self, element, text, enter=True):
        for c in text:
            element.send_keys(c)
            # time.sleep(0.01)
        if enter:
            element.send_keys(Keys.ENTER)

    def get_any_game(self):
        response = requests.get("https://www.chess.com/service/gamelist/top/rapid")
        game_id = response.json()[0]["legacyId"]
        return self.url(f"game/live/{game_id}")

    def follow(self, driver, player, screenshot=False):
        chat_input = None
        try:
            chat_input = driver.find_element(
                By.XPATH, "//input[@data-cy='chat-input-field']"
            )
        except NoSuchElementException:
            pass
        if not chat_input:
            chat_input = self._get_chat(driver)
        chat_num = len(driver.find_elements(By.CLASS_NAME, "console-message-component"))
        self.type_slow(chat_input, f"/follow {player}")
        WebDriverWait(driver, 10).until(
            lambda driver: len(
                driver.find_elements(By.CLASS_NAME, "console-message-component")
            )
            >= chat_num + 2
        )
        result = driver.find_elements(By.CLASS_NAME, "console-message-component")[
            -1
        ].text

        return result

    def _get_chat(self, driver):
        game_url = self.get_any_game()
        driver.get(game_url)
        chat_input = WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//input[@data-cy='chat-input-field']")
            )
        )
        return chat_input

    def _get_ping(self, driver, chat_input, player, retry=False):
        chat_num = len(driver.find_elements(By.CLASS_NAME, "console-message-component"))
        self.type_slow(chat_input, f"/ping {player}")
        try:
            WebDriverWait(driver, 3).until(
                lambda driver: len(
                    driver.find_elements(By.CLASS_NAME, "console-message-component")
                )
                >= chat_num + 2
            )
        except TimeoutException:
            if retry:
                print("retrying ping")
                chat_input = self._get_chat(driver)
                return self._get_ping(driver, chat_input, player, retry=False)
            else:
                raise

    def ping(self, driver, player):
        uuid = self.get_uuid(player)
        if not uuid:
            return "Invalid chess.com username"
        chat_input = None
        try:
            chat_input = driver.find_element(
                By.XPATH, "//input[@data-cy='chat-input-field']"
            )
        except NoSuchElementException:
            pass
        if not chat_input:
            chat_input = self._get_chat(driver)

        self._get_ping(driver, chat_input, player, retry=True)
        result = driver.find_elements(By.CLASS_NAME, "console-message-component")[
            -1
        ].text

        return result

    def screenshot(self, driver, name="debug"):
        import boto3
        from selenium.webdriver.common.by import By

        dt_string = datetime.now(timezone.utc).strftime("%d-%m-%Y-%H:%M:%S")
        s3 = boto3.client("s3")
        el = driver.find_element(By.TAG_NAME, "body")
        el.screenshot(f"/tmp/{name}.png")
        s3.upload_file(
            f"/tmp/{name}.png",
            os.environ["SCREENSHOT_BUCKET"],
            f"{name}-{dt_string}.png",
            ExtraArgs=dict(ContentType="image/png"),
        )
