from commands.browser.base import BrowserCommand
from crawlers.browser import ChesscomCrawler


class Follow(BrowserCommand):
    id = "follow"

    def get_result(self, driver, params):
        crawler = ChesscomCrawler()
        return crawler.follow(driver, params["player"], params["screenshot"])
