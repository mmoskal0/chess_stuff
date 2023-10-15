from commands.base import Command
from crawlers.websockets import WebsocketCrawler


class Opening(Command):
    id = "ping"

    def get_result(self, params):
        player = params["player"]
        crawler = WebsocketCrawler(init=True)
        return crawler.get_ping(player)
