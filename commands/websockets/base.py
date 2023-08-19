import websocket

from commands.base import Command


class WebsocketCommand(Command):
    id = None

    def __init__(self):
        self.ws = websocket.WebSocket()
