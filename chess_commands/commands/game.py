from commands.base import Command
from commands.emojis import Emoji
from crawlers.browser import ChesscomCrawler


class Game(Command):
    id = "game"

    def get_result(self, params):
        player = params["player"]
        crawler = ChesscomCrawler()
        game_id = self.get_game_id(player)
        return f"{Emoji.black_pawn} {crawler.get_game_url(game_id)}"
