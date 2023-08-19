import json
import os
import time

import requests


class WebsocketCrawler:
    def __init__(self):
        self.client_id = None
        self.cookie_value = os.environ["CHESSCOM_REMEMBERME"]
        self.id = 1

    @property
    def cookie(self):
        return {"CHESSCOM_REMEMBERME": self.cookie_value}

    @property
    def session_cookie(self):
        r = requests.get(
            f"https://www.chess.com/callback/user/navigation-data", cookies=self.cookie
        )
        session_cookie = requests.utils.dict_from_cookiejar(r.cookies)["PHPSESSID"]
        return f"PHPSESSID={session_cookie}"

    def connect(self, ws):
        ws.connect(
            "wss://live2.chess.com/cometd",
            origin="https://www.chess.com",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)",
            cookie=self.session_cookie,
            timeout=2,
        )

    def send(self, ws, message):
        message["id"] = str(self.id)
        self.id += 1
        ws.send(json.dumps(message))

    def handshake(self, ws):
        message_handshake = {
            "version": "1.0",
            "minimumVersion": "1.0",
            "channel": "/meta/handshake",
            "supportedConnectionTypes": ["ssl-websocket"],
            "advice": {"timeout": 60000, "interval": 0},
            "clientFeatures": {
                "protocolversion": "2.1",
                "clientname": "LC6;chrome/114.0.0;Mac OS;elmf7a6;47.0.1",
                "skiphandshakeratings": True,
                "adminservice": True,
                "announceservice": True,
                "arenas": True,
                "chessgroups": True,
                "clientstate": True,
                "events": True,
                "gameobserve": True,
                "genericchatsupport": True,
                "genericgamesupport": True,
                "guessthemove": True,
                "multiplegames": True,
                "multiplegamesobserve": True,
                "offlinechallenges": True,
                "pingservice": True,
                "playbughouse": True,
                "playchess": True,
                "playchess960": True,
                "playcrazyhouse": True,
                "playkingofthehill": True,
                "playoddschess": True,
                "playthreecheck": True,
                "privatechats": True,
                "stillthere": True,
                "teammatches": True,
                "tournaments": True,
                "userservice": True,
            },
            "serviceChannels": ["/service/user"],
            "ext": {
                "ack": True,
                "timesync": {"tc": int(time.time() * 1000), "l": 0, "o": 0},
            },
            "id": "1",
            "clientId": None,
        }
        # perform handshake to obtain clientId
        self.send(ws, message_handshake)
        response = ws.recv()
        response = json.loads(response)
        self.client_id = response[0]["clientId"]

    def refresh(self, ws):
        message_connect = {
            "channel": "/meta/connect",
            "connectionType": "ssl-websocket",
            "ext": {
                "ack": 1,
                "timesync": {"tc": int(time.time() * 1000), "l": 50, "o": 0},
            },
            "id": "",
            "clientId": self.client_id,
        }
        self.send(ws, message_connect)

    def get_game_moves(self, ws, game_id):
        message_sub = {
            "channel": "/meta/subscribe",
            "subscription": f"/game/{game_id}",
            "id": "",
            "clientId": self.client_id,
            "ext": {
                "ack": 1,
                "timesync": {"tc": int(time.time() * 1000), "l": 50, "o": 0},
            },
        }
        self.send(ws, message_sub)
        self.refresh(ws)

        while r := ws.recv():
            r = json.loads(r)
            if r[0]["channel"] == f"/game/{game_id}":
                break

        return r[0]["data"]["game"]["moves"]
