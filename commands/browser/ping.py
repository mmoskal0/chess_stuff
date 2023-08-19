from commands.browser.base import BrowserCommand
from crawlers.browser import ChesscomCrawler


class Ping(BrowserCommand):
    id = "ping"

    def get_result(self, driver, params):
        crawler = ChesscomCrawler()
        return crawler.ping(driver, params["player"])
