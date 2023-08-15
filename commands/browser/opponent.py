from commands.browser.base import BrowserCommand
from crawlers.chesscom import ChesscomCrawler


class Opponent(BrowserCommand):
    id = "opponent"

    def get_result(self, driver, params):
        player = params["player"]
        crawler = ChesscomCrawler()
        activity = crawler.get_user_activity(player)
        status, game_id = crawler.get_activity_status(activity)
        if not game_id:
            return f"{player} is {status}"

        player1, player2 = crawler.players(driver, game_id)
        if player.lower() == player1.lower():
            return crawler.get_member_url(player2)
        elif player.lower() == player2.lower():
            return crawler.get_member_url(player1)
