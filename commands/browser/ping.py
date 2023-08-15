from commands.browser.base import BrowserCommand
from crawlers.chesscom import ChesscomCrawler


class Ping(BrowserCommand):
    id = "ping"

    def get_result(self, driver, params):
        crawler = ChesscomCrawler()
        return crawler.ping(driver, params["player"])
