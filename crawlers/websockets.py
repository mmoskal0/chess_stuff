import json
import os
import time

import requests
import websocket


class WebsocketCrawler:
    def __init__(self, init=False):
        self.client_id = None
        self.cookie_value = os.environ["CHESSCOM_REMEMBERME"]
        self.id = 1
        self.ws = websocket.WebSocket()
        if init:
            self.init()

    def init(self):
        self.connect()
        self.handshake()

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

    def connect(self):
        self.ws.connect(
            "wss://live2.chess.com/cometd",
            origin="https://www.chess.com",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)",
            cookie=self.session_cookie,
            timeout=4,
        )

    def send(self, message):
        message["id"] = str(self.id)
        self.id += 1
        self.ws.send(json.dumps(message))

    def recv(self):
        ret = self.ws.recv()
        print(ret)
        return ret

    def handshake(self):
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
        self.send(message_handshake)
        response = self.recv()
        response = json.loads(response)
        self.client_id = response[0]["clientId"]

    def refresh(self):
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
        self.send(message_connect)

    def get_game_moves(self, game_id):
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
        self.send(message_sub)
        self.refresh()

        while r := self.recv():
            r = json.loads(r)
            if r[0]["channel"] == f"/game/{game_id}":
                break

        return r[0]["data"]["game"]["moves"]

    def get_ping(self, player):
        self.refresh()
        while r := self.recv():
            r = json.loads(r)
            if r[0]["channel"] == "/meta/connect":
                break

        message_ping = {
            "channel": "/service/user",
            "data": {"tid": "QueryLagInfo", "uid": player},
            "id": "",
            "clientId": self.client_id,
        }
        self.send(message_ping)
        self.recv()
        self.refresh()
        time.sleep(2)
        while r := self.recv():
            r = json.loads(r)
            if r[0]["channel"] == "/service/user" and "lagms" in r[0].get("data", {}):
                break
        ping = r[0]["data"]["lagms"]
        status = r[0]["data"]["user"]["status"]
        player = r[0]["data"]["user"]["uid"]

        return f"Ping {player}: {f'{ping} ms' if ping else status}"
