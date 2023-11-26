from chess_commands.commands.browser.base import BrowserCommand
from chess_commands.crawlers.browser import ChesscomCrawler


class Opening(BrowserCommand):
    id = "opening_deprecated"

    def get_result(self, driver, params):
        player = params["player"]
        crawler = ChesscomCrawler()
        activity = crawler.get_user_activity(player)
        status, game_id = crawler.get_activity_status(activity)
        if not game_id:
            return f"{player} is {status}"

        return crawler.opening(driver, game_id, params["screenshot"])