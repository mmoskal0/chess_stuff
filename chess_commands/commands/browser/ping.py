from chess_commands.commands.browser.base import BrowserCommand
from chess_commands.crawlers.browser import ChesscomCrawler


class Ping(BrowserCommand):
    id = "ping_deprecated"

    def get_result(self, driver, params):
        crawler = ChesscomCrawler()
        return crawler.ping(driver, params["player"])
