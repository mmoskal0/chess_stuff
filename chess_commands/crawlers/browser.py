import json
import os
import time
from urllib.parse import urljoin

import requests

chess_uuids = {
    "annamaja": "160ee19e-830f-11e5-800a-000000000000",
    "hannahsayce": "fd91f7ea-7479-11e9-8e68-69b78e4292d1",
}


# TODO
# Split this class into BrowserCrawler and regular API
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

    def get_user_details(self, username):
        response = requests.get(f"https://www.chess.com/callback/user/popup/{username}")
        return response.json()

    def get_uuid(self, username):
        global chess_uuids
        if username in chess_uuids:
            print("HIT CACHE FOR UUID")
            return chess_uuids[username]

        try:
            uuid = self.get_user_details(username)["uuid"]
            chess_uuids[username] = uuid
        except:
            uuid = None
        return uuid

    def is_valid_username(self, username):
        uuid = self.get_uuid(username)
        return bool(uuid)

    def get_game_url(self, game_id):
        return self.url(f"game/live/{game_id}")

    def get_player_stats(self, username):
        r = requests.get(f"https://www.chess.com/callback/member/stats/{username}")
        return r.json()

    def get_score(self, player1_id, player2_id):
        r = requests.get(
            f"https://www.chess.com/callback/user/lifetime-score/{player1_id}/{player2_id}",
            cookies=self.cookie,
        )
        return r.json()

    def get_user_activity(self, username):
        uuid = self.get_uuid(username)
        r = requests.get(
            f"https://www.chess.com/service/presence/users?ids={uuid}",
            cookies=self.cookie,
        )
        return r.json()["users"]

    def get_user_activity_stream(self, username):
        uuid = self.get_uuid(username)
        r = requests.get(
            f"https://www.chess.com/service/presence/watch/users?ids={uuid}",
            cookies=self.cookie,
            stream=True,
        )
        return r.iter_lines(decode_unicode=True)

    def get_activity_status_stream(self, activity):
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

    def get_activity_status(self, activity):
        status, game_id = None, None
        for data in activity:
            if data["status"] != "online":
                status = "not online"
                return status, game_id, None
            if data["activity"] != "playing":
                status = "online but not playing"
                return status, game_id, None
            game_id = data["activityContext"]["games"][0]["legacyId"]
            stream_url = data.get("streaming", {}).get("url")
            return status, game_id, stream_url

    def get_stream_url(self, player):
        activity = self.get_user_activity(player)
        status, game_id, stream_url = self.get_activity_status(activity)
        return stream_url

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

    def get_member_url(self, username):
        return self.url(f"member/{username.lower()}")

    def get_any_game(self):
        response = requests.get("https://www.chess.com/service/gamelist/top/rapid")
        game_id = response.json()[0]["legacyId"]
        return self.url(f"game/live/{game_id}")
