from commands.websockets.base import WebsocketCommand
from crawlers.websockets import WebsocketCrawler


class Opening(WebsocketCommand):
    id = "ping"

    def get_result(self, params):
        player = params["player"]
        crawler = WebsocketCrawler()
        crawler.connect(self.ws)
        crawler.handshake(self.ws)
        return crawler.get_ping(self.ws, player)
