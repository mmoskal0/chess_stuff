from commands.base import Command
from commands.emojis import Emoji
from crawlers.websockets import WebsocketCrawler


class Opening(Command):
    id = "ping"

    @staticmethod
    def format_result(data):
        ping = int(data["lagms"])
        status = data["user"]["status"]
        player = data["user"]["uid"]

        return f"{Emoji.bars} Ping {player}: {f'{ping} ms' if ping else status}"

    def get_result(self, params):
        player = params["player"]
        crawler = WebsocketCrawler(init=True)
        result = crawler.get_ping(player)
        return self.format_result(result)
