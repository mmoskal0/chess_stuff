from chess_commands.commands.browser.base import BrowserCommand
from chess_commands.crawlers.browser import ChesscomCrawler


class Follow(BrowserCommand):
    id = "follow"

    def get_result(self, driver, params):
        crawler = ChesscomCrawler()
        return crawler.follow(driver, params["player"], params["screenshot"])
