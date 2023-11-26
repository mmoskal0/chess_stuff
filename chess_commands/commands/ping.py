from chess_commands.commands.base import Command
from chess_commands.crawlers.websockets import WebsocketCrawler


class Opening(Command):
    id = "ping"

    @staticmethod
    def format_result(data):
        ping = data["lagms"]
        status = data["user"]["status"]
        player = data["user"]["uid"]

        return f"Ping {player}: {f'{ping} ms' if ping else status}"

    def get_result(self, params):
        player = params["player"]
        crawler = WebsocketCrawler(init=True)
        result = crawler.get_ping(player)
        return self.format_result(result)
