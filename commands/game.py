from commands.base import Command
from crawlers.chesscom import ChesscomCrawler


class Game(Command):
    id = "game"

    def get_result(self, params):
        player = params["player"]
        crawler = ChesscomCrawler()
        activity = crawler.get_user_activity(player)
        if activity is None:
            return "Invalid chess.com username"
        status, game_id = crawler.get_activity_status(activity)
        if game_id:
            return crawler.get_game_url(game_id)
        else:
            return f"{player} is {status}"
